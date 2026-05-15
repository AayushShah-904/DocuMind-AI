# DocuMind AI

A production-grade, full-stack Retrieval-Augmented Generation (RAG) application. Upload PDFs, DOCX, and TXT documents, ask natural-language questions, and get instant answers powered by Gemini 2.5 Flash, with inline source citations.

## 🚀 Features

- **Document Processing Pipeline**: Fast uploading, parsing, cleaning, and chunking.
- **Hybrid Search**: Fuses MongoDB Atlas Vector Search (semantic) with keyword matching using Reciprocal Rank Fusion (RRF).
- **Cross-Encoder Reranking**: Boosts retrieval precision using `ms-marco-MiniLM-L-6-v2`.
- **Streaming LLM Responses**: FastAPI SSE streaming straight to a Next.js frontend, generating token-by-token.
- **Source Citations**: Every answer is grounded in exact document chunks for full transparency.
- **SaaS-Grade UI**: Clean, professional aesthetic using Tailwind CSS and Framer Motion.

## 🛠️ Tech Stack

**Backend**:
- Python 3.11, FastAPI
- LangChain, `langchain-google-genai` (Gemini 2.5 Flash)
- MongoDB Atlas (Vector Search), Beanie ODM
- Sentence Transformers (`all-MiniLM-L6-v2` for embeddings)
- Redis (Caching & Rate Limiting)

**Frontend**:
- Next.js 14 (App Router)
- React Query, Zustand
- Tailwind CSS, shadcn/ui primitives

**DevOps**:
- Docker & Docker Compose
- Nginx Reverse Proxy
- GitHub Actions CI

## 📦 Local Setup

### 1. Prerequisites
- Docker & Docker Compose installed
- A free [MongoDB Atlas](https://www.mongodb.com/cloud/atlas) account
- A free [Google AI Studio](https://aistudio.google.com/) API Key

### 2. Environment Variables
Copy the example env files and fill in your credentials:

```bash
# Backend
cp backend/.env.example backend/.env
# Edit backend/.env and add your MONGODB_URI and GEMINI_API_KEY

# Frontend
cp frontend/.env.local.example frontend/.env.local
```

### 3. Database Setup (MongoDB Atlas)
1. Create a free M0 cluster.
2. In Atlas, go to **Search** -> **Create Search Index**.
3. Create a **Vector Search Index** on the `documind.chunks` collection named `vector_index`:
```json
{
  "fields": [{
    "type": "vector",
    "path": "embedding",
    "numDimensions": 384,
    "similarity": "cosine"
  }, {
    "type": "filter",
    "path": "user_id"
  }]
}
```

### 4. Run the Application
```bash
docker-compose up --build
```
The app will be available at [http://localhost](http://localhost).

## 📊 Benchmarks
Run the evaluation script to measure p50/p95 latency and precision metrics:
```bash
cd backend
python scripts/benchmark.py
```

## 🏗️ Architecture
```text
Browser ──► Nginx ──► FastAPI Backend ──► MongoDB Atlas (Vector + Data)
                  └──► Next.js Frontend       └── Redis (Cache/Rate-limit)
```

## 📄 License
MIT
