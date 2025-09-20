from fastapi import FastAPI, File, UploadFile, HTTPException
from pydantic import BaseModel
from app.llm import SESSIONS, SYSTEM_PROMPT, get_history, chat_once
from typing import Optional
from io import BytesIO
import PyPDF2
import uuid

app = FastAPI(title="Simple Chat API")


class AskPayload(BaseModel): #to define JSON schema for request body
    question: str
    session_id: Optional[str] = None
    max_new_tokens: Optional[int] = 100
    temperature: Optional[float] = 0.1


class NewSessionResponse(BaseModel): #this is used to genereta new session id
    session_id: str


# get the list of items - pdf files
@app.get("/ping")
def root():
    return {"ok": True}

@app.get("/")
def redirect():
    return "Go to:  http://127.0.0.1:8000/docs"

@app.post("/session/new", response_model=NewSessionResponse)
def new_session():
    sid = uuid.uuid4().hex #random
    SESSIONS[sid] = [{"role": "system", "content": SYSTEM_PROMPT}]
    return {"session_id": sid}


@app.post("/ask")
def ask(payload: AskPayload):
    sid = payload.session_id or uuid.uuid4().hex
    hist = get_history(sid)
    try:
        answer = chat_once(
            hist,
            payload.question,
            max_new_tokens=payload.max_new_tokens or 100,
            temperature=payload.temperature or 0.1,
        )
        return {"session_id": sid, "answer": answer}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/session/{session_id}/history")
def get_history_api(session_id: str):
    return {"history": get_history(session_id)}


@app.post("/upload_docs")
async def upload_file(
    file: Optional[UploadFile] = File(...)
):
    if not file:
        raise HTTPException(status_code=400, detail="No file uploaded")

    try:
        content = await file.read()
        pdf_stream = BytesIO(content)
        reader = PyPDF2.PdfReader(pdf_stream)
        text = ""
        for page in reader.pages:
            text += page.extract_text() or ""

        return {"filename": file.filename, "text": text[:1000]}
    except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")
