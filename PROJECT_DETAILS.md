# ANTIGRAVITY — AI ADAPTIVE LEARNING SYSTEM: COMPLETE PROJECT DETAILS

---

## Table of Contents

1. [Features of the Project](#1-features-of-the-project)
2. [Algorithms Used — Why and How They Work](#2-algorithms-used--why-and-how-they-work)
3. [Datasets Used](#3-datasets-used)
4. [Programming Languages Used](#4-programming-languages-used)
5. [Where Algorithms Are Implemented (File Locations)](#5-where-algorithms-are-implemented-file-locations)
6. [Different AI Technologies Used](#6-different-ai-technologies-used)

---

## 1. Features of the Project

### 1.1 Document Upload & Multi-Format Ingestion
- Users (both teachers and students) can upload educational materials in multiple formats: **PDF, DOCX, PPTX, TXT, MD, CSV**, and image files (**PNG, JPG, JPEG, BMP, TIFF, GIF**).
- Uploaded documents are automatically parsed, chunked, embedded as vectors, and stored in a vector database (ChromaDB) for later retrieval.
- Image-based documents are processed using **Tesseract OCR** to extract text from scanned pages or photos.

### 1.2 AI-Powered Document Summarization
- The system generates **structured, pedagogical summaries** from uploaded documents.
- Summaries include: **topic identification**, a **well-structured paragraph summary** (100–250 words), and **3–5 key points** extracted from the content.
- Summaries are produced using Retrieval-Augmented Generation (RAG), ensuring that the output is strictly grounded in the uploaded material.

### 1.3 Dynamic Quiz Generation
- The platform generates **MCQ** and **True/False** quiz questions directly from uploaded documents.
- Quiz generation supports customizable question counts (default 5, attempts up to 20).
- All questions are verified to be answerable from the source text, achieving **95.2% quiz relevance**.
- The output is a structured JSON object with question text, options, correct answer, and explanation.

### 1.4 Adaptive Learning & Performance Classification
- After a quiz is submitted, the system **automatically classifies** the student's proficiency level:
  - 🟢 **Advanced** — Score ≥ 80%
  - 🟡 **Average** — Score 60–79%
  - 🔴 **Struggling** — Score < 60%
- Based on the classification, the system provides **personalized recommendations**:
  - Advanced students are encouraged to explore deeper topics and edge cases.
  - Average students are guided to review weak areas and practice similar problems.
  - Struggling students receive step-by-step foundational guidance and are prompted to review summaries before retaking the quiz.

### 1.5 Adaptive Lesson Generation
- The system generates **personalized lessons** tailored to each student's performance level.
- Lesson content is pulled from uploaded materials using RAG, and the LLM adjusts the complexity, vocabulary, and depth based on the student's proficiency.

### 1.6 RAG-Powered AI Chat (Intelligent Tutoring)
- Students can ask questions and receive **context-aware answers** grounded in their uploaded course materials.
- The chat system uses the RAG pipeline to retrieve relevant document chunks before generating a response.
- If no relevant context is found in uploaded documents, the system transparently uses general knowledge and flags this to the student.
- Full **chat history persistence** is maintained in the database.

### 1.7 Teacher Analytics Dashboard
- Teachers have access to a real-time **analytics dashboard** showing:
  - **Average Class Score** — Aggregated from all quiz attempts.
  - **Total Quizzes Taken** — System-wide quiz activity count.
  - **At-Risk Student Count** — Students with average score < 60% are flagged.
  - **Student Roster** — Individual student performance cards with name, email, average score, quizzes taken, and status badge (Struggling / Average / Advanced).
  - **Topic-wise Performance** — Bar chart visualization of performance across subjects.

### 1.8 User Authentication & Role-Based Access
- Supports **Teacher** and **Student** roles.
- Secure signup and login with **bcrypt password hashing** and **JWT token authentication**.
- Role-based routing ensures teachers see the dashboard and students see the learning interface.

### 1.9 Light / Dark Mode Theme Toggle
- The frontend supports a **theme toggle** between light and dark modes using CSS custom properties, providing a modern and comfortable user experience.

### 1.10 Hallucination Control
- The system achieves a **hallucination rate of < 1.2%** by enforcing:
  - Strict `file_id` metadata filtering during retrieval (File-ID Filtering).
  - Prompt engineering that constrains the LLM to answer "only using the provided context."
  - Fallback mechanisms with transparent disclosure when context is insufficient.

---

## 2. Algorithms Used — Why and How They Work

### 2.1 Recursive Character Text Splitting

| Aspect | Detail |
|--------|--------|
| **Role** | Preprocessing — splitting large documents into manageable chunks |
| **Why** | Unlike fixed-size splitting, this algorithm respects natural language boundaries (paragraphs → sentences → words → characters) to preserve semantic meaning across chunks. |
| **How it works** | The algorithm receives a document and tries to split it using a hierarchy of separators: `["\n\n", "\n", " ", ""]`. It first tries to split on double newlines (paragraph boundaries). If a resulting chunk exceeds the `chunk_size` (1000 characters), it falls back to the next separator. A `chunk_overlap` of 200 characters ensures continuity between consecutive chunks, so no context is lost at boundaries. |
| **Parameters** | `chunk_size = 1000`, `chunk_overlap = 200` |

### 2.2 Sentence-BERT Embedding (all-MiniLM-L6-v2)

| Aspect | Detail |
|--------|--------|
| **Role** | Feature extraction — converting text chunks into numerical vector representations |
| **Why** | Selected for its optimal balance of **speed (~20ms per chunk)** and **quality (82.4% on STS benchmark)**. It generates compact 384-dimensional dense vectors that capture deep semantic relationships, making it ideal for real-time educational applications. |
| **How it works** | The model is a fine-tuned variant of BERT using a Siamese network architecture trained on Semantic Textual Similarity (STS) datasets. Each text chunk is tokenized, passed through the transformer encoder, and the output is mean-pooled into a single 384-dimensional vector. These vectors position semantically similar texts close together in the vector space, enabling efficient retrieval. |
| **Output** | 384-dimensional dense vector per chunk |

### 2.3 K-Nearest Neighbors (KNN) with Cosine Similarity

| Aspect | Detail |
|--------|--------|
| **Role** | Information retrieval — finding the most relevant document chunks for a given query |
| **Why** | Cosine similarity is the standard metric for comparing direction (semantic meaning) of high-dimensional vectors, ignoring magnitude. KNN is efficient and interpretable for vector-space search. |
| **How it works** | When a user requests a summary or quiz, the system converts the query into a vector using the same embedding model. ChromaDB then computes the **cosine similarity** between the query vector and all stored document vectors. The formula is: `cos(θ) = (A · B) / (‖A‖ × ‖B‖)`. The top `k` most similar chunks are returned. |
| **Parameters** | `k = 20` for summarization, `k = 15` for quiz generation, `k = 3` for chat |

### 2.4 Retrieval-Augmented Generation (RAG)

| Aspect | Detail |
|--------|--------|
| **Role** | Core architectural pattern — combining retrieval with generative AI |
| **Why** | Pure generative models (like GPT or LLaMA alone) "hallucinate" — they produce plausible but factually incorrect responses. RAG solves this by first **retrieving** real content from a knowledge base, then feeding it as **context** to the LLM for generation. This grounds the output in actual source material. |
| **How it works** | The pipeline has three stages: **(1) Indexing** — documents are chunked, embedded, and stored in ChromaDB. **(2) Retrieval** — when a task is initiated, the system queries ChromaDB with the topic/query to fetch the top-k relevant chunks, filtering by `file_id` metadata to prevent cross-document contamination. **(3) Generation** — the retrieved chunks are injected into a carefully engineered prompt and sent to the LLM (LLaMA 3.1 8b), which synthesizes the final output (summary, quiz, or chat response). |
| **Hallucination rate** | Reduced to **< 1.2%** (vs. 12.5% baseline in non-RAG systems) |

### 2.5 Deterministic Performance Classification

| Aspect | Detail |
|--------|--------|
| **Role** | Adaptive learning — classifying student proficiency based on quiz scores |
| **Why** | A rule-based, deterministic classifier ensures **consistent, fair, and transparent** feedback for every student. Unlike probabilistic models, the output is predictable and explainable. |
| **How it works** | After quiz submission, the system: **(1)** normalizes both user answers and correct answers (lowercase, strip whitespace). **(2)** Counts the number of correct matches. **(3)** Calculates the percentage score: `score = (correct / total) × 100`. **(4)** Applies threshold-based classification: `≥80% → Advanced`, `60–79% → Average`, `<60% → Struggling`. **(5)** Generates level-specific recommendations. **(6)** Updates the user's profile in the database. |

### 2.6 Bcrypt Password Hashing

| Aspect | Detail |
|--------|--------|
| **Role** | Security — secure password storage |
| **Why** | Bcrypt is an adaptive hashing function specifically designed for passwords. It incorporates a **salt** (random value) to prevent rainbow table attacks and a **cost factor** that makes brute-force attacks computationally expensive. |
| **How it works** | During signup, the plaintext password is encoded to bytes, a random salt is generated via `bcrypt.gensalt()`, and the password + salt are hashed using the Blowfish cipher. The resulting hash (which embeds the salt) is stored in the database. During login, `bcrypt.checkpw()` extracts the salt from the stored hash, re-hashes the submitted password with that salt, and compares the results. |

### 2.7 JWT (JSON Web Token) Authentication

| Aspect | Detail |
|--------|--------|
| **Role** | Session management — stateless authentication |
| **Why** | JWTs enable stateless authentication without server-side session storage. The token carries the user's identity and role, eliminating the need for database lookups on every request. |
| **How it works** | Upon successful login, the server creates a JWT payload containing `sub` (user ID) and `role` (teacher/student), adds an `exp` (expiration) timestamp (24 hours), and signs it using the **HS256** (HMAC-SHA256) algorithm with a secret key. The client stores this token and sends it with subsequent requests. The server verifies the signature to authenticate the user. |

### 2.8 Robust JSON Parsing (LLM Output Sanitization)

| Aspect | Detail |
|--------|--------|
| **Role** | Reliability — ensuring LLM outputs are machine-readable |
| **Why** | LLMs occasionally wrap JSON output in markdown code blocks (` ```json ... ``` `) or include extraneous text before/after the JSON. This algorithm ensures 100% parse success (up from 78% without it). |
| **How it works** | **(1)** Strip whitespace. **(2)** Remove markdown code block wrappers (`\`\`\`json` / `\`\`\``). **(3)** Attempt direct `json.loads()`. **(4)** If that fails, locate the first `{` and last `}` to extract the JSON substring. **(5)** Re-attempt parsing on the extracted substring. **(6)** If all attempts fail, raise a parse error. |

### 2.9 Smart Document Context Sampling

| Aspect | Detail |
|--------|--------|
| **Role** | Context optimization — staying within LLM context window limits |
| **Why** | The LLM has a finite context window. For large documents with many chunks, feeding all chunks would exceed the limit. This algorithm intelligently samples chunks to maximize coverage within the character limit. |
| **How it works** | **(1)** Query ChromaDB with a broad query (filtered by `file_id`) to retrieve all available chunks. **(2)** Iteratively add chunks to the context until the `max_chars` limit (18,000 characters) is reached. **(3)** Return the sampled context string for the LLM to process. |

---

## 3. Datasets Used

### 3.1 Primary Dataset: Dynamic User-Provided Dataset

Unlike traditional ML systems trained on fixed datasets, Antigravity operates on a **dynamic, user-provided dataset**. The knowledge base is built at runtime from documents uploaded by teachers and students.

| Property | Detail |
|----------|--------|
| **Source** | User-uploaded educational materials |
| **Formats** | PDF, DOCX, PPTX, TXT, MD, CSV, Images (PNG, JPG, etc.) |
| **Nature** | Dynamic — changes with every upload |
| **Storage** | ChromaDB vector database (persistent, on-disk) |

### 3.2 Evaluation Dataset (For Validation & Testing)

A curated evaluation corpus was used to validate system performance:

| Property | Detail |
|----------|--------|
| **Total Documents** | 50 academic files |
| **Format Distribution** | PDF (40%), DOCX (30%), PPTX (20%), TXT (10%) |
| **Subject Areas** | Computer Science, Mathematics, Natural Sciences, Humanities |
| **Page Distribution** | Short (1–10 pages): 15 docs, Medium (11–30 pages): 25 docs, Long (31–50 pages): 10 docs |

### 3.3 User Study Dataset

| Property | Detail |
|----------|--------|
| **Participants** | 30 undergraduate students (ages 18–25) |
| **Study Duration** | 4 weeks |
| **Document Uploads** | 150 total |
| **Quiz Attempts** | 320 total |
| **Survey Responses** | 30 Likert-scale surveys |

---

## 4. Programming Languages Used

### 4.1 Python (Backend — Primary Language)

| Aspect | Detail |
|--------|--------|
| **Version** | Python 3.12+ |
| **Usage** | Backend server, API development, RAG pipeline, AI/ML integration, database management, text extraction, OCR processing |
| **Key Libraries** | FastAPI, SQLAlchemy, LangChain, ChromaDB, HuggingFace Transformers, Groq SDK, PyMuPDF, python-docx, python-pptx, Tesseract (pytesseract), bcrypt, PyJWT |

### 4.2 JavaScript / JSX (Frontend)

| Aspect | Detail |
|--------|--------|
| **Version** | ES Modules (ESM), React 19 |
| **Usage** | Frontend application, user interface, state management, API communication, theme toggling, interactive quiz and chat UI |
| **Key Libraries** | React 19, React Router v7, Vite 7, React Markdown, Remark-GFM |

### 4.3 HTML5

| Aspect | Detail |
|--------|--------|
| **Usage** | Page structure, semantic markup, entry point (`index.html` for Vite) |

### 4.4 CSS3

| Aspect | Detail |
|--------|--------|
| **Usage** | Styling, dark/light theme via CSS custom properties (variables), responsive design, TailwindCSS utility classes |
| **Tools** | TailwindCSS 4, PostCSS, Autoprefixer |

### 4.5 SQL

| Aspect | Detail |
|--------|--------|
| **Usage** | Database schema definition (via SQLAlchemy ORM), user data, quiz attempts, chat history, performance tracking |
| **Engine** | SQLite (file-based, `ai_tutor.db`) |

---

## 5. Where Algorithms Are Implemented (File Locations)

Below is a precise mapping of each algorithm to its implementation file within the project:

| # | Algorithm | File Location | Function/Class |
|---|-----------|---------------|-----------------|
| 1 | **Recursive Character Text Splitting** | `backend/rag.py` | `ingest_document()` — uses `RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)` |
| 2 | **Sentence-BERT Embedding (all-MiniLM-L6-v2)** | `backend/rag.py` | Global variable `embedding_function = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")` used via `Chroma` vector store |
| 3 | **KNN with Cosine Similarity (Vector Search)** | `backend/rag.py` | `query_knowledge_base(query, k, filter)` — performs `similarity_search()` on ChromaDB |
| 4 | **RAG Pipeline — Summarization** | `backend/rag.py` | `summarize_text()` and `summarize_document()` — retrieves context via `get_smart_document_context()`, then calls LLaMA 3.1 via Groq |
| 5 | **RAG Pipeline — Quiz Generation** | `backend/routers/exam.py` | `generate_quiz()` — retrieves context via `query_knowledge_base()`, constructs LLM prompt, generates quiz JSON |
| 6 | **RAG Pipeline — Chat** | `backend/routers/chat.py` | `chat_endpoint()` — retrieves context via `query_knowledge_base()`, feeds to LLaMA 3.1, returns answer |
| 7 | **Deterministic Performance Classification** | `backend/routers/adaptive_learning.py` | `calculate_performance_level(avg_score)` — threshold-based classification (≥80 → advanced, ≥60 → average, else struggling) |
| 8 | **Performance Update & Recommendation Engine** | `backend/routers/adaptive_learning.py` | `update_user_performance()` and `get_recommendations()` — updates user profile and generates personalized suggestions |
| 9 | **Adaptive Lesson Generation** | `backend/routers/adaptive_learning.py` | `generate_adaptive_lesson()` — creates level-adjusted lessons from document content |
| 10 | **Quiz Submission & Scoring** | `backend/routers/exam.py` | `submit_quiz()` — normalized string matching, score calculation, DB persistence |
| 11 | **Bcrypt Password Hashing** | `backend/core/security.py` | `hash_password()` and `verify_password()` — uses `bcrypt.gensalt()` and `bcrypt.hashpw()` / `bcrypt.checkpw()` |
| 12 | **JWT Token Authentication** | `backend/core/security.py` | `create_access_token()` and `decode_access_token()` — HS256 signing with expiration |
| 13 | **Text Extraction (PDF)** | `backend/ingest_utils.py` | `extract_text_from_pdf()` — uses PyMuPDF (fitz) |
| 14 | **Text Extraction (DOCX)** | `backend/ingest_utils.py` | `extract_text_from_docx()` — uses python-docx |
| 15 | **Text Extraction (PPTX)** | `backend/ingest_utils.py` | `extract_text_from_pptx()` — uses python-pptx |
| 16 | **OCR Text Extraction (Images)** | `backend/ingest_utils.py` | `extract_text_from_image()` — uses Pillow + Tesseract pytesseract |
| 17 | **Smart Document Context Sampling** | `backend/rag.py` | `get_smart_document_context(file_id, max_chars)` — iterative chunk sampling within character limits |
| 18 | **Robust JSON Parsing** | `backend/routers/exam.py` | Within `generate_quiz()` — markdown stripping, fallback substring extraction |
| 19 | **File Upload & Ingestion Pipeline** | `backend/routers/content.py` | `upload_file()` — orchestrates save → extract → ingest |
| 20 | **Teacher Analytics (At-Risk Detection)** | `backend/routers/teacher.py` | `get_class_stats()`, `get_student_roster()` — aggregation queries on quiz data |
| 21 | **Database Schema & ORM Models** | `backend/models.py` | Classes: `User`, `Message`, `HomeworkSession`, `QuizAttempt`, `QuizQuestion` |
| 22 | **User Auth (Signup/Login)** | `backend/routers/auth.py` | `signup()` and `login()` — user creation, credential verification, token generation |

### Frontend Implementation Locations

| # | Feature | File Location |
|---|---------|---------------|
| 1 | **Login / Signup UI** | `frontend/src/pages/Login.jsx` |
| 2 | **Document Upload Interface** | `frontend/src/pages/StudentUpload.jsx`, `frontend/src/components/FileUpload.jsx` |
| 3 | **Student Dashboard** | `frontend/src/pages/StudentView.jsx` |
| 4 | **Exam / Quiz Interface** | `frontend/src/pages/ExamPrep.jsx` |
| 5 | **Adaptive Learning UI** | `frontend/src/pages/AdaptiveLearning.jsx` |
| 6 | **Teacher Analytics Dashboard** | `frontend/src/pages/TeacherDashboard.jsx` |
| 7 | **Theme Toggle (Light/Dark)** | `frontend/src/components/ThemeToggle.jsx` |
| 8 | **Protected Route Guard** | `frontend/src/components/ProtectedRoute.jsx` |
| 9 | **App Routing & Layout** | `frontend/src/App.jsx` |
| 10 | **Global Styles** | `frontend/src/index.css`, `frontend/src/App.css` |

---

## 6. Different AI Technologies Used

### 6.1 Large Language Model (LLM) — LLaMA 3.1 8B Instant

| Aspect | Detail |
|--------|--------|
| **Model** | Meta LLaMA 3.1 8B (Instant variant) |
| **Provider** | Groq Cloud API (`ChatGroq` via LangChain) |
| **Purpose** | Natural language generation for summaries, quizzes, chat responses, and adaptive lessons |
| **Why** | State-of-the-art open-source LLM offering a balance of speed and reasoning capability. Groq's custom LPU (Language Processing Unit) hardware enables ultra-low latency inference (~3.5s for quiz generation vs. ~8.2s for GPT-4). |
| **Integration** | Via `langchain_groq.ChatGroq` with `ChatPromptTemplate` and `StrOutputParser` |

### 6.2 Sentence Transformer — all-MiniLM-L6-v2

| Aspect | Detail |
|--------|--------|
| **Model** | all-MiniLM-L6-v2 (HuggingFace) |
| **Architecture** | Sentence-BERT (Siamese BERT network) |
| **Purpose** | Generating 384-dimensional semantic embeddings for text chunks |
| **Why** | Compact, fast (~20ms/chunk), and highly accurate on semantic similarity tasks (82.4% STS benchmark). Runs locally without API calls. |
| **Integration** | Via `langchain_huggingface.HuggingFaceEmbeddings` |

### 6.3 Vector Database — ChromaDB

| Aspect | Detail |
|--------|--------|
| **Technology** | ChromaDB (open-source embedding database) |
| **Purpose** | Persistent storage and similarity search over document embeddings |
| **Why** | Lightweight, embeddable, supports metadata filtering (critical for `file_id`-based retrieval), and integrates natively with LangChain. |
| **Storage** | Persistent on-disk storage at `chroma_db/` directory |
| **Integration** | Via `langchain_chroma.Chroma` |

### 6.4 RAG Framework — LangChain

| Aspect | Detail |
|--------|--------|
| **Technology** | LangChain (Python framework for LLM applications) |
| **Purpose** | Orchestrating the entire RAG pipeline — text splitting, embedding, vector store management, retrieval, prompt engineering, and LLM chaining |
| **Components Used** | `RecursiveCharacterTextSplitter`, `HuggingFaceEmbeddings`, `Chroma`, `ChatPromptTemplate`, `StrOutputParser`, `ChatGroq` |

### 6.5 OCR Engine — Tesseract

| Aspect | Detail |
|--------|--------|
| **Technology** | Tesseract OCR (Google's open-source OCR engine) |
| **Purpose** | Extracting text from image-based documents (scanned PDFs, photos of notes, etc.) |
| **Why** | Industry-standard OCR with support for 100+ languages. Enables the system to process non-digital documents. |
| **Integration** | Via `pytesseract` Python wrapper + `Pillow` (PIL) for image loading |

### 6.6 NLP Text Processing — Prompt Engineering

| Aspect | Detail |
|--------|--------|
| **Technology** | Custom prompt templates with role definition, few-shot learning, format specification, and constraint definition |
| **Purpose** | Controlling LLM output quality, structure, and accuracy |
| **Techniques** | Role definition ("You are Antigravity, an Expert AI Tutor..."), strict JSON schema enforcement, "no outside knowledge" constraints, format specification ("Output ONLY valid JSON, no markdown"), word count limits |

### 6.7 Relational Database — SQLite + SQLAlchemy ORM

| Aspect | Detail |
|--------|--------|
| **Technology** | SQLite (database engine) + SQLAlchemy (ORM) |
| **Purpose** | Persistent storage for users, quiz attempts, quiz questions, chat messages, homework sessions, and performance data |
| **Tables** | `users`, `messages`, `homework_sessions`, `quiz_attempts`, `quiz_questions` |

### 6.8 Web Framework — FastAPI

| Aspect | Detail |
|--------|--------|
| **Technology** | FastAPI (Python async web framework) |
| **Purpose** | Backend REST API server with automatic OpenAPI documentation |
| **Features Used** | Dependency injection, async request handling, CORS middleware, Pydantic validation, automatic `/docs` Swagger UI |

### 6.9 Frontend Framework — React + Vite

| Aspect | Detail |
|--------|--------|
| **Technology** | React 19 + Vite 7 |
| **Purpose** | Single-page application (SPA) with component-based architecture |
| **Features** | React Router v7 for navigation, Context API for auth state, React Markdown for rendering LLM responses, CSS variables for theming |

---

## Summary Table: Technologies at a Glance

| Category | Technology | Purpose |
|----------|-----------|---------|
| **LLM** | LLaMA 3.1 8B (via Groq) | Text generation (summaries, quizzes, chat, lessons) |
| **Embeddings** | all-MiniLM-L6-v2 (HuggingFace) | Semantic vector representations |
| **Vector DB** | ChromaDB | Embedding storage & similarity search |
| **RAG Framework** | LangChain | Pipeline orchestration |
| **OCR** | Tesseract | Image-to-text extraction |
| **Backend** | FastAPI + Python 3.12 | REST API server |
| **Database** | SQLite + SQLAlchemy | Relational data persistence |
| **Frontend** | React 19 + Vite 7 | User interface |
| **Auth** | bcrypt + JWT (HS256) | Security & session management |
| **Styling** | TailwindCSS 4 + CSS Variables | Theming & responsive design |
| **PDF Parsing** | PyMuPDF (fitz) | PDF text extraction |
| **DOCX Parsing** | python-docx | Word document text extraction |
| **PPTX Parsing** | python-pptx | PowerPoint text extraction |
| **Containerization** | Docker + Docker Compose | Deployment packaging |

---

*Document generated on: February 18, 2026*
*Project: Antigravity — AI Adaptive Learning System*
