# 🎓 AI Tutor – Full Stack Adaptive AI Learning Platform  
## Complete Final-Year Project Kit (Academic / Educational Use Only)

AI Tutor is a **full-stack adaptive learning and exam preparation system** designed to transform static study materials into an interactive, personalized learning experience using Artificial Intelligence.

This project demonstrates **real-world AI system design** through Retrieval-Augmented Generation (RAG), performance-based adaptation, and analytics dashboards.  
It is **review-ready, demo-ready, and viva-ready**, intended strictly for **academic and educational purposes**.

---

## 🎯 Project Objective

Traditional AI chatbots suffer from:
- Hallucinated responses
- No performance tracking
- No adaptive learning paths
- Lack of teacher-level insights

**AI Tutor addresses these limitations by:**
- Generating summaries and quizzes strictly from uploaded documents (RAG)
- Tracking learner performance automatically
- Adapting explanations and recommendations dynamically
- Providing analytics dashboards for monitoring and intervention

---

## ✨ Core Features

### 📚 Learning & Assessment
- Upload PDFs, DOCX, PPTX, TXT, and image files
- AI-generated summaries with adaptive length
- MCQ and True/False quiz generation
- Performance-based learner categorization:
  - 🔴 Struggling
  - 🟡 Average
  - 🟢 Advanced

### 🧠 Adaptive AI System
- RAG-powered AI chat grounded in user documents
- Adaptive recommendations based on quiz scores
- Homework assistance with step-by-step guidance

### 📊 Teacher Analytics Dashboard
- Topic-wise performance visualization
- At-risk student identification
- Real-time class insights
- Demo data included for presentations and evaluations

### 🎨 User Experience
- Clean, modern UI
- Light / Dark mode support
- Responsive design

---

## 🧱 Technology Stack

### Backend
- **Python 3.12**
- **FastAPI**
- **Groq LLM API** (LLaMA 3.1 – Instant)
- **ChromaDB** (Vector Store for RAG)
- **HuggingFace Embeddings** (all-MiniLM-L6-v2)
- **SQLite**
- **Tesseract OCR** (for image-based documents)

### Frontend
- **React 18**
- **Vite**
- **React Router**
- **CSS Variables (Light/Dark Theme)**

---

## 📁 Project Structure

AI-Tutor-Complete-Final-Year-Project-Kit/
│
├── Backend/
│ ├── main.py
│ ├── rag.py
│ ├── models.py
│ ├── schemas.py
│ ├── routers/
│ ├── requirements.txt
│ └── .env.example
│
├── Frontend/
│ ├── src/
│ ├── package.json
│ └── vite.config.js
│
└── README.md

---

## 🚀 Local Setup Instructions

### Prerequisites
- Python **3.12+**
- Node.js **18+**
- Tesseract OCR (for image document support)

---

### Backend Setup

```bash
cd Backend
python -m venv venv
```

Activate the environment:

**Windows**
```bash
.\venv\Scripts\activate
```

**macOS / Linux**
```bash
source venv/bin/activate
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Create environment file:
```bash
cp .env.example .env
```

Add your API key inside .env:
```ini
GROQ_API_KEY=your_api_key_here
```

Run backend:
```bash
uvicorn main:app --reload
```
Backend URL: `http://127.0.0.1:8000`
API Documentation: `http://127.0.0.1:8000/docs`

---

### Frontend Setup

```bash
cd Frontend
npm install
npm run dev
```

Frontend URL: `http://localhost:5173`

### 🐳 Docker (Optional)

```bash
docker-compose up --build
```
Ensure the .env file is configured before building containers.

---

## 🔑 Environment Variables

Create `Backend/.env` with the following:

```ini
GROQ_API_KEY=your_groq_api_key_here
```

Free API keys can be obtained from:  
https://console.groq.com

---

## ⚠️ Important Academic Disclaimer
This project is intended strictly for academic and educational use

No commercial SaaS license is provided

No personalized installation, customization, or debugging support is included

Users are expected to have basic knowledge of Python and JavaScript

---

## 📌 Notes for Viva / Evaluation
- Demonstrates RAG-based hallucination control
- Implements adaptive learning logic
- Uses modular full-stack architecture
- Includes analytics and performance monitoring
- Suitable for AI / ML / CS / IT final-year evaluation