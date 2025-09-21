from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from app.llm import get_history, chat_once
from app.RAG import RAG, extract_text_from_pdf, preview_chunk
from app.session_manager import create_session, get_session_docs, get_session_history, add_document_to_session
from app.VectorStore import VectorStore
from typing import Optional

app = FastAPI(title="Simple Chat API")


class AskPayload(BaseModel):  # to define JSON schema for request body
    # question: str
    # session_id: Optional[str] = None
    max_new_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.1


class NewSessionResponse(BaseModel):  # this is used to genereta new session id
    session_id: str


@app.post("/session/new", response_model=NewSessionResponse)
def new_session():
    sid = create_session()
    return {"session_id": sid}


@app.post("/ask")
def ask(payload: AskPayload,
        question: Optional[str] = None,
        session_id: Optional[str] = None):
    question = "" if question is None else question
    sid = session_id or create_session()
    hist = get_session_history(sid)
    docs = get_session_docs(sid)
    context_chunks = []
    if docs:
        vs = VectorStore()
        for fname, chunks in docs.items():
            vs.add_document(fname, chunks)
        results = vs.query(question, k=3)
        context_chunks = [r["chunk"] for r in results]
    if context_chunks:
        context = "\n".join(context_chunks)
        prompt = f"Context:\n{context}\n\nQuestion: {question}"
    else:
        prompt = question
    answer = chat_once(
        hist,
        prompt,
        max_new_tokens=payload.max_new_tokens or 100,
        temperature=payload.temperature or 0.1,
    )
    return {"session_id": session_id, "answer": answer}


@app.post("/upload_docs")
async def upload_file(
    file: Optional[UploadFile] = File(...),  # noqa: B008
    session_id: Optional[str] = None
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    sid = session_id or create_session()
    content = await file.read()
    text = extract_text_from_pdf(content)
    chunks = RAG(text=text, filename=file.filename)
    if not chunks:
        raise HTTPException(status_code=422, detail="No text extracted or chunking produced 0 chunks.")
    add_document_to_session(sid, file.filename, chunks)
    return {
        "session_id": sid,
        "filename": file.filename,
        "num_chunks": len(chunks),
        "avg_chunk_len": sum(len(c) for c in chunks) // len(chunks),
        "first_chunk_preview": preview_chunk(chunks[0]),
        "last_chunk_preview": preview_chunk(chunks[-1])
    }


# get the list of items - pdf files
@app.get("/ping")
def root():
    return {"ok": True}


@app.get("/")
def redirect():
    return "Go to:  http://127.0.0.1:8000/docs"


@app.get("/session/{session_id}/history")
def get_history_api(session_id: str):
    return {"history": get_history(session_id)}
