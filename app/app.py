
from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

from app.llm import chat_once, rag_add_context_if_docs
from app.rag import extract_text_from_pdf, preview_chunk, rag
from app.session_manager import add_document_to_session, create_session, get_session_docs, get_session_history

app = FastAPI(title="Simple Chat API")


class AskPayload(BaseModel):  # to define JSON schema for request body
    # question: str
    # session_id: Optional[str] = None
    max_new_tokens: int | None = 50
    temperature: float | None = 0.1


class NewSessionResponse(BaseModel):  # this is used to genereta new session id
    session_id: str


@app.post("/ask_question")
def ask_question(payload: AskPayload,
        question: str | None = None,
        session_id: str | None = None):
    question = "" if question is None else question
    sid = session_id or create_session()
    prompt = rag_add_context_if_docs(sid, question)
    answer = chat_once(
        sid,
        prompt,
        max_new_tokens=payload.max_new_tokens or 100,
        temperature=payload.temperature or 0.1,
    )
    return {"session_id": sid, "answer": answer}


@app.post("/upload_docs")
async def upload_file(
    file: UploadFile | None = File(...),  # noqa: B008
    session_id: str | None = None
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")
    sid = session_id or create_session()
    content = await file.read()
    text = extract_text_from_pdf(content)
    chunks = rag(text=text, filename=file.filename)
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


@app.get("/session/{session_id}/history")
def session_history(session_id: str):
    return {"history": get_session_history(session_id)}


@app.get("/session/{session_id}/docs")
def session_docs(session_id: str):
    docs = get_session_docs(session_id)
    return {"docs": list(docs.keys())}


@app.post("/session/new", response_model=NewSessionResponse)
def new_session():
    sid = create_session()
    return {"session_id": sid}


@app.get("/ping")
def root():
    return {"ok": True}


@app.get("/")
def redirect():
    return "Go to:  http://127.0.0.1:8000/docs"
