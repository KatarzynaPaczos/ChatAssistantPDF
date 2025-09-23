
import re
from io import BytesIO

import pypdf
from sentence_transformers import SentenceTransformer

from app.session_manager import get_session_docs
from app.vector_store import VectorStore

MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
embedder = SentenceTransformer(MODEL_NAME)
tokenizer = embedder.tokenizer

def clean_text(txt: str) -> str:
    """
    Cleaning - new line normalisation, erase doubble space
    """
    if not txt:
        return ""
    t = txt.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"-\n(\w)", r"\1", t)       # join word breaks
    t = re.sub(r"\n{2,}", "\n\n", t)       # collapse multi blank lines
    t = re.sub(r"(?<!\n)\n(?!\n)", " ", t) # single newline → space
    t = re.sub(r"[ \t]{2,}", " ", t)       # collapse multiple spaces/tabs
    return t.strip()


def chunk_text(text: str, max_tokens: int = 100, overlap: int = 20) -> list[str]:
    """
    Split text into overlapping chunks by tokens.
    Each chunk is cleaned and flattened.
    """
    text = clean_text(text)
    tokens = tokenizer.encode(text, add_special_tokens=False)

    chunks = []
    start = 0
    while start < len(tokens):
        end = min(start + max_tokens, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk = tokenizer.decode(chunk_tokens, skip_special_tokens=True)
        chunk = " ".join(chunk.split())  # flatten stray whitespace/newlines
        chunks.append(chunk)

        if end == len(tokens):
            break
        start = end - overlap  # slide window with overlap

    return chunks


def rag(text: str, filename: str | None):
    chunks = chunk_text(text, max_tokens=100, overlap=20)
    model = VectorStore(embedder=embedder)
    model.add_document(filename, chunks)
    return chunks


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a PDF file (bytes)."""
    pdf_stream = BytesIO(pdf_bytes)
    reader = pypdf.PdfReader(pdf_stream)
    text_parts = []
    for page in reader.pages:
        raw = page.extract_text() or ""
        cleaned = clean_text(raw)
        text_parts.append(cleaned)
    return "\n\n".join(text_parts).strip()


def preview_chunk(chunk: str, length: int = 200) -> str:
    """Return a preview of a chunk (first N chars)."""
    return chunk[:length] if chunk else ""


def rag_add_context_if_docs(sid: str, question: str):
    '''add new item to historey with the context'''
    chunks_all = get_session_docs(sid)
    context_chunks = []
    if chunks_all:
        vs = VectorStore(embedder=embedder)
        for fname, chunks in chunks_all.items():
            vs.add_document(fname, chunks)
        results = vs.query(question, k=2)
        context_chunks = [r["chunk"] for r in results]
        context = "\n".join(context_chunks)
        return f"Context: {context}. Based on the above context, answer the following question: {question}"
    else:
        return question
