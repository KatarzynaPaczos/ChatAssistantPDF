import uuid

# Stores chat history and uploaded document chunks per session
SESSIONS: dict[str, list[dict]] = {}  # chat history {session_id,=: [prompts]}
SESSION_DOCS: dict[str, dict[str, list[str]]] = {}
# {session_id: {filename: chunks}} - stores uploaded docs per session
SYSTEM_PROMPT = "Answer briefly in English. If you don't know, say you don't know. Never invent or guess."
start_message = {"role": "system", "content": SYSTEM_PROMPT}
MAX_TURNS = 3  # when the history is too long (more than MAX_TURNS turns), cut it


def create_session(sid: str | None = None) -> str:
    """Create a new session and initialize its stores."""
    if sid is None:
        sid = uuid.uuid4().hex
    SESSIONS[sid] = [start_message]
    SESSION_DOCS[sid] = {}
    return sid


def get_session_history(session_id: str) -> list[dict]:
    """Get chat history for a session, or initialize if missing."""
    if session_id not in SESSIONS:
        create_session(session_id)
    SESSIONS[session_id] = clamp_history(SESSIONS[session_id])
    return SESSIONS[session_id]


def get_session_docs(session_id: str) -> dict[str, list[str]]:
    """Get uploaded docs for a session, or initialize if missing."""
    if session_id not in SESSION_DOCS:
        create_session(session_id)
    return SESSION_DOCS[session_id]


def add_document_to_session(session_id: str,
                            filename: str | None,
                            chunks: list[str]):
    """Add document chunks to a session."""
    docs = get_session_docs(session_id)
    remove_session_history(session_id)
    docs[str(filename)] = chunks


def clamp_history(history):
    '''clamp the history when longer than MAX_TURNS - my model is weak due to hardware restrictions'''
    sys = history[0:1] if history and history[0]["role"] == "system" else []
    rest = history[1:] if sys else history
    trimmed = rest[-MAX_TURNS*2:]# here - but user x3 maybe...
    return sys + trimmed


def remove_session_history(session_id):
    SESSIONS[session_id] = [start_message]
