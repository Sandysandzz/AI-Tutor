# AI Tutor - Quick Setup Guide

## Prerequisites
- Python 3.12+  (https://www.python.org/downloads/)
- Node.js 18+   (https://nodejs.org/)
- Tesseract OCR (optional, for image documents) https://github.com/UB-Mannheim/tesseract/wiki

---

## Step 1 - Backend

Open a terminal, navigate to this folder, then run:

  cd backend
  python -m venv venv

Activate the environment:
  Windows:       .\venv\Scripts\activate
  macOS/Linux:   source venv/bin/activate

Install dependencies:
  pip install -r requirements.txt

Configure your API key:
  Edit  backend/.env  and set your Groq API key.
  (Free key from https://console.groq.com)
  The .env file is pre-configured; only update if the key expires.

Start the backend:
  uvicorn main:app --reload --port 8000

Backend    ->  http://127.0.0.1:8000
API Docs   ->  http://127.0.0.1:8000/docs

---

## Step 2 - Frontend

Open a SECOND terminal:

  cd frontend
  npm install       # installs dependencies (first time only)
  npm run dev       # starts Vite dev server

Frontend   ->  http://localhost:5173

---

## Step 3 - Open the App

Navigate to http://localhost:5173 in your browser.

The database (ai_tutor.db) and vector store (chroma_db/) are pre-included,
so all existing accounts, documents, and quiz history are ready immediately.

---

## Docker (Alternative)

  docker-compose up --build

Make sure backend/.env has a valid GROQ_API_KEY before building.

---

## Important Folders

  chroma_db/    ChromaDB vector store (RAG embeddings) - do NOT delete
  uploads/      Uploaded student/teacher documents     - do NOT delete
  ai_tutor.db   SQLite database (users, sessions, quiz history) - do NOT delete

## One-Click Start (Windows)

Run  start_windows.ps1  from PowerShell after completing Steps 1 and 2 once.
