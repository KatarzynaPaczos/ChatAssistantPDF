
from typing import List, Optional
from app.VectorStore import VectorStore
from io import BytesIO
import PyPDF2
import re


def clean_text(txt: str) -> List[str]:
    """
    Cleaning - new line normalisation, erase doubble space
    """
    if not txt:  # paragraf brakes gone!!!!!!!
        return []
    t = txt.replace("\r\n", "\n").replace("\r", "\n")  # Normalize Windows/Mac newlines to Unix '\n'
    t = re.sub(r"-\n(\w)", r"\1", t)  # join breaks in the middle of words "-\nX" -> "X"
    t = re.sub(r"\n{3,}", "\n\n", t)  # Turn 3+ newlines into exactly two (one blank line = paragraph break)
    t = re.sub(r"(?<!\n)\n(?!\n)", " ", t)  # SINGLE \n -> space
    t = re.sub(r"[ \t]{2,}", " ", t)  # Collapse multiple spaces or tabs to a single space
    sentences = re.split(r'(?<=[.!?])\s+', t)  # divide by sentences
    return [s.strip() for s in sentences if s.strip()]


def chunk_text(text: str, max_chars: int = 100, overlap: int = 10) -> List[str]:
    """
    Chuns -> section -> doubble /n
    """
    paragrafs = clean_text(text)
    if not paragrafs or len(paragrafs) == 0:
        return []

    # paragraphs = [p.strip() for p in re.split(r"\n{2,}", text) if p.strip()]
    chunks = []
    buf = ""
    for p in paragrafs:
        if not buf:
            buf = p
        elif len(buf) + 2 + len(p) <= max_chars:
            buf = buf + "\n\n" + p
        else:
            chunks.append(buf)
            tail = buf[-overlap:] if overlap > 0 and len(buf) > overlap else ""
            buf = (tail + ("\n\n" if tail else "") + p).strip()
    if buf:
        chunks.append(buf)

    # if long blocks - split them  up
    final = []
    for c in chunks:
        if len(c) <= max_chars:
            final.append(c)
        else:
            start = 0
            while start < len(c):
                end = min(start + max_chars, len(c))
                final.append(c[start:end])
                if end == len(c):
                    break
                start = max(0, end - overlap)
    return final


def RAG(text: str, filename: Optional[str]):
    chunks = chunk_text(text, max_chars=200, overlap=100)
    model = VectorStore()
    model.add_document(filename, chunks)
    query = "Who is the author of that doc?"
    response = model.query(query, k=3)
    print(response)
    return chunks


def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Extract text from a PDF file (bytes)."""
    pdf_stream = BytesIO(pdf_bytes)
    reader = PyPDF2.PdfReader(pdf_stream)
    text = ""
    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text
    return text


def preview_chunk(chunk: str, length: int = 400) -> str:
    """Return a preview of a chunk (first N chars)."""
    return chunk[:length] if chunk else ""
