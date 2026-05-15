# Development Log - DocuMind AI

## Architecture & Infrastructure Decisions

### 1. MongoDB Atlas for Vector Search & Data Storage
- **Decision:** Use MongoDB Atlas as the unified database for both application data (users, document metadata) and vector embeddings.
- **Rationale:** Reduces infrastructure complexity compared to running a separate vector database (like Pinecone or Milvus) alongside a primary database. MongoDB's vector search integration allows us to filter by `user_id` and semantic similarity in a single query seamlessly.

### 2. FastAPI for Backend
- **Decision:** Built the backend using FastAPI (Python).
- **Rationale:** Native support for async operations makes it perfect for streaming Server-Sent Events (SSE) from the LLM (Gemini 2.5 Flash). Python is the dominant language in the AI ecosystem, making integration with LangChain and HuggingFace models straightforward.
- **Challenges Overcome:** Faced `pydantic-core` build failures due to an unsupported beta Python version (3.14). Transitioned to a stable Python version (3.11) which resolved C-extension compilation errors.

### 3. Next.js App Router for Frontend
- **Decision:** Chosen for the frontend framework using the App Router.
- **Rationale:** React Server Components allow us to handle environment variables securely and optimize page loads. It also integrates very cleanly with FastAPI's streaming endpoints to provide a real-time typing effect in the UI.
- **Challenges Overcome:** Resolved module path resolution (`@/` aliases) and strict environment variable bindings to ensure a seamless production build.

### 4. Background Processing for Document Ingestion
- **Decision:** Shifted PDF/DOCX parsing, chunking, and embedding logic to background tasks.
- **Rationale:** Processing large files synchronously blocked the FastAPI event loop, causing timeouts and unresponsive endpoints. Background processing ensures the API remains responsive while heavy NLP tasks (like running `ms-marco-MiniLM-L-6-v2` locally) happen asynchronously.

### 5. Dockerized Nginx Reverse Proxy
- **Decision:** Packaged the system using Docker Compose with an Nginx reverse proxy routing traffic.
- **Rationale:** Simplifies local development and production deployment by serving both the Next.js frontend (on `/`) and FastAPI backend (on `/api`) on the same domain and port, completely eliminating CORS (Cross-Origin Resource Sharing) headaches.
