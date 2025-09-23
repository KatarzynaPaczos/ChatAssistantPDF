# Chat Assistant (PDF‑aware)

A small FastAPI backend that lets you ask natural-language questions about your own PDFs. It runs locally, finds the most relevant parts of your documents, and uses that context to generate short answers.

---

## What it does (in simple terms)

1. **Upload a PDF** → the app extracts and cleans the text, splits it into small overlapping chunks, and builds a vector index.
2. **Ask a question** → it searches the chunks for the best matches and adds them as **context** to the prompt.
3. **Get a short answer** → a small local LLM responds using that context. Sessions keep separate docs and brief chat history.

---

## Tech stack

- **Python** • FastAPI for the API layer
- **Transformers + PyTorch** for the small instruction‑tuned LLM
- **SentenceTransformers + FAISS** for embeddings and vector search
- **PyPDF2** for PDF text extraction
- **uv** for running the app locally (any standard Python env also works)
- **Docker**/**Compose** (optional) for containerized runs

---

## Key features

- **Practical RAG**: retrieval‑augmented generation with clear, readable code. After upload, text is cleaned (newline normalization, hyphen joins), token‑chunked, embedded, and stored in FAISS. On each question, the top matches are retrieved and prepended as context before generation.
- **Local‑first LLM**: default model is a tiny instruction‑tuned transformer (fast, laptop‑friendly). You can swap the model name for a bigger one if you have more resources.
- **Per‑session isolation**: each session has its own documents and short chat history. Uploading new docs resets the conversation for that session. In‑memory storage keeps things simple.
- **Token‑aware chunking**: small chunks (with overlap) to improve retrieval quality without blowing up context size.
- **Straightforward code layout**:
  - `app.py` — FastAPI endpoints
  - `llm.py` — model load, prompt building, generation
  - `rag.py` — PDF extract/clean, token chunking
  - `session_manager.py` — sessions, docs, short history
  - `vector_store.py` — embeddings + FAISS
  - `main.py` — run in API or CLI mode

---

## Quick start

### Run locally

```bash
# Start the API
uv run python main.py api
# Open the docs UI:
# http://127.0.0.1:8000/docs
```

CLI mode is also available - only to talk to LLM:

```bash
uv run python main.py cli
```

### With Docker (optional)

```bash
# Export deps and build
uv export --frozen --no-dev --no-cache -o requirements.txt
docker build -t chat-assistant-pdf .
docker run -p 8000:8000 chat-assistant-pdf

# Or with Compose
docker compose up --build
```

### Run dev
To check code style and function names before committing, run:
```bash
uv run bash run_checks.sh
```
To run tests:
```bash
uv run bash run_tests.sh
```

To-do – next steps:
* Create HTML for chatting with AI
* Write more tests
* Expand to all extensions, not only PDF
