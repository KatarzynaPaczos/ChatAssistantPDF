import uuid
from typing import Dict, List, Optional

# Stores chat history and uploaded document chunks per session
SESSIONS: Dict[str, List[dict]] = {} #chat history {session_id, [prompts]}
SESSION_DOCS: Dict[str, Dict[str, List[str]]] = {}# {session_id: {filename: chunks}} - stores uploaded docs per session

def create_session() -> str:
    """Create a new session and initialize its stores."""
    sid = uuid.uuid4().hex
    SESSIONS[sid] = []
    SESSION_DOCS[sid] = {}
    '''
    sid = uuid.uuid4().hex #random
    SESSIONS[sid] = [{"role": "system", "content": SYSTEM_PROMPT}]
    SESSION_DOCS[sid] = {}
    '''
    return sid

def get_session_history(session_id: str) -> List[dict]:
    """Get chat history for a session, or initialize if missing."""
    if session_id not in SESSIONS:
        SESSIONS[session_id] = []
    return SESSIONS[session_id]

def get_session_docs(session_id: str) -> Dict[str, List[str]]:
    """Get uploaded docs for a session, or initialize if missing."""
    if session_id not in SESSION_DOCS:
        SESSION_DOCS[session_id] = {}
    return SESSION_DOCS[session_id]

def add_document_to_session(session_id: str, filename: Optional[str], chunks: List[str]):
    """Add document chunks to a session."""
    docs = get_session_docs(session_id)
    docs[str(filename)] = chunks

def list_session_files(session_id: str) -> List[str]:
    """List filenames uploaded in a session."""
    docs = get_session_docs(session_id)
    return list(docs.keys())