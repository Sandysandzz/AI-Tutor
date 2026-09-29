import os
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
import json

# --- Configuration ---
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FAISS_DB_DIR = os.path.join(PROJECT_ROOT, "faiss_db")

embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")

# Load existing FAISS index or create a new one
if os.path.exists(FAISS_DB_DIR) and os.path.exists(os.path.join(FAISS_DB_DIR, "index.faiss")):
    vector_store = FAISS.load_local(FAISS_DB_DIR, embedding_function, allow_dangerous_deserialization=True)
else:
    # Initialize with an empty document so FAISS has something to infer dimension from.
    vector_store = FAISS.from_texts(["Initializing FAISS"], embedding_function)

def ingest_document(file_path: str, text_content: str):
    """
    Splits text into chunks and adds them to the vector store.
    """
    if not text_content:
        return 0

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )
    texts = text_splitter.split_text(text_content)

    filename = os.path.basename(file_path)
    docs = [
        Document(page_content=t, metadata={"source": filename, "chunk_index": i})
        for i, t in enumerate(texts)
    ]

    if docs:
        vector_store.add_documents(docs)
        vector_store.save_local(FAISS_DB_DIR)
    
    return len(docs)

def query_knowledge_base(query: str, k: int = 3, filter: dict = None):
    # FAISS filter format expects a dict of metadata to match, identical to what chroma does simply.
    results = vector_store.similarity_search(query, k=k, filter=filter)
    return results

def get_smart_document_context(file_id: str, max_chars: int = 18000):
    """
    Retrieves a 'smart' context using STRICT sampling to stay under limits.
    """
    try:
        # FAISS doesn't have a direct 'get documents by metadata' API that returns everything cleanly, 
        # so we fetch from the internal docstore.
        docstore = vector_store.docstore._dict
        
        chunks = []
        for doc_id, doc in docstore.items():
            if doc.metadata.get("source") == file_id:
                chunks.append({"text": doc.page_content, "index": doc.metadata.get("chunk_index", 999999)})
        
        if not chunks:
            return ""
            
        chunks.sort(key=lambda x: x["index"])
        
        full_docs = [c["text"] for c in chunks]
        total_docs = len(full_docs)
        
        if total_docs == 0:
            return ""
            
        full_text = "\n\n".join(full_docs)
        
        if len(full_text) <= max_chars:
            return full_text
            
        avg_chunk_size = len(full_text) / (total_docs + 1)
        max_chunks = int(max_chars / avg_chunk_size)
        
        if max_chunks >= total_docs:
             return full_text
             
        start_alloc = max(1, int(max_chunks * 0.20))
        end_alloc = max(1, int(max_chunks * 0.10))
        middle_alloc = max_chunks - start_alloc - end_alloc
        
        if middle_alloc < 0:
             middle_alloc = 0
             
        selected_indices = set()
        
        for i in range(min(start_alloc, total_docs)):
            selected_indices.add(i)
        
        for i in range(max(0, total_docs - end_alloc), total_docs):
            selected_indices.add(i)
            
        middle_start = start_alloc
        middle_end = max(start_alloc, total_docs - end_alloc)
        sample_range = middle_end - middle_start
        
        if sample_range > 0 and middle_alloc > 0:
            step = sample_range / middle_alloc
            for i in range(middle_alloc):
                idx = int(middle_start + i * step)
                if idx < total_docs:
                    selected_indices.add(idx)
        
        final_indices = sorted(list(selected_indices))
        selected_docs = [full_docs[i] for i in final_indices]
        
        final_context = "\n\n".join(selected_docs)
        return final_context
        
    except Exception as e:
        print(f"Error in smart context retrieval: {e}")
        return ""

def summarize_text(text: str, max_length: int = 400):
    """
    Generate a Pedagogical Summary formatted with HTML tags using strict user-defined JSON schema.
    """
    api_key = os.getenv("GROQ_API_KEY")
    if not api_key:
        raise RuntimeError("GROQ_API_KEY not set")

    llm = ChatGroq(model="llama-3.1-8b-instant", temperature=0.3, api_key=api_key)
    
    prompt = ChatPromptTemplate.from_template("""
SYSTEM: You are an expert AI Tutor. You will be given extracted content from a document. Produce a single JSON object (no extra text) in the exact format described below. Follow every rule strictly.

OUTPUT JSON schema (MUST match exactly):
{{
  "topic": "<short title, max 8-10 words>",
  "summary_paragraphs": ["<paragraph1>", "<paragraph2>", "<paragraph3>"],
  "key_points": [
    {{ "term": "<2-6 words>", "explanation": "<one concise sentence>" }}
  ]
}}

FORMAT RULES (strict):
1. Return ONLY the JSON object and nothing else. Do NOT wrap in markdown, backticks, comments, or additional explanation.
2. "topic": one short title that best captures the document.
3. "summary_paragraphs": an ARRAY of 3–4 paragraphs. Each array element is one paragraph string. The **total** length across paragraphs should be about **300–450 words** (aim ~350 words).
   - Paragraphs must be clear, student-friendly, and non-repetitive.
   - Use HTML <strong> tags around key terms or formulas (e.g., <strong>Bayes' theorem</strong>) — this is for frontend rendering.
   - Keep sentences varied and well-structured; do not output a single long line.
4. "key_points": an ARRAY of **8–12** objects.
   - Each object must have exactly two keys: "term" and "explanation".
   - "term": a 2–6 word label (no HTML tags).
   - "explanation": one short sentence (10–20 words) that may include <strong> around the term once.
5. Use only facts present in the provided content. Do not hallucinate external facts.
6. Remove page numbers, file names, and metadata. Do not mention that you are summarizing.
7. If the provided content lacks coverage for 4 paragraphs, synthesize only from available content but still aim for total ~250–350 words.
8. If content is long, compress and synthesize — extract the highest-value concepts, not every minor point.
9. Avoid duplicate sentences or duplicate key_points (exact or paraphrased).
10. No extra keys allowed in the JSON.

Now, given the following content between the markers, produce the JSON exactly:

<<<CONTENT>>>
{text}
<<<CONTENT>>>
""")
    
    chain = prompt | llm | StrOutputParser()
    
    try:
        safe_text = text[:18000]
        response = chain.invoke({"text": safe_text})
        
        response = response.strip()
        if response.startswith("```json"):
            response = response[7:]
        if response.startswith("```"):
            response = response[3:]
        if response.endswith("```"):
            response = response[:-3]
        response = response.strip()
        
        try:
            result = json.loads(response)
            return result
        except json.JSONDecodeError as json_err:
            print(f"JSON parse error: {json_err}")
            return {
                "topic": "Error",
                "summary_paragraphs": ["Summarization failed to produce valid JSON."],
                "key_points": []
            }
            
    except Exception as e:
        print(f"Summarize text error: {e}")
        return {
            "topic": "Error",
            "summary_paragraphs": [f"Service is busy. Please try again. Error: {str(e)}"],
            "key_points": []
        }

def summarize_document(file_id: str, max_length: int = 500):
    """
    Summarizes a document using strict sampling.
    """
    full_text = get_smart_document_context(file_id, max_chars=18000)
    
    if not full_text:
        return {"summary_paragraphs": ["No text found."], "key_points": [], "topic": "Empty"}
    
    return summarize_text(full_text, max_length)
