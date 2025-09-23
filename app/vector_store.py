from typing import Any

import faiss
from sentence_transformers import SentenceTransformer


class VectorStore:
    def __init__(self, embedder: SentenceTransformer):
        self.embedder =  embedder
        self.dim = self.embedder.get_sentence_embedding_dimension()
        self.index = faiss.IndexFlatL2(self.dim)
        # mapping: internal ID → metadata (chunk text, filename, etc.)
        self.id2meta: dict[int, dict[str, Any]] = {}
        self.next_id = 0  # id of the chunk - next free

    def add_document(self, filename: str | None, chunks: list[str]):
        """Embed and add all chunks of a document to the index."""
        embeddings = self.embedder.encode(chunks, convert_to_numpy=True, show_progress_bar=False)
        self.index.add(embeddings)  # type: ignore
        # store mapping
        for i, chunk in enumerate(chunks):
            self.id2meta[self.next_id + i] = {
                "filename": filename,
                "chunk": chunk
            }  # to track - wchoch chunk is from which document
        self.next_id += len(chunks)

    def query(self, question: str, k: int = 3) -> list[dict[str, Any]]:
        """Search for most relevant chunks to a query."""
        q_emb = self.embedder.encode([question], convert_to_numpy=True)
        distances, indices = self.index.search(q_emb, k)  # type: ignore
        results = []
        for idx, dist in zip(indices[0], distances[0], strict=False):
            if idx == -1:  # no match
                continue
            meta = self.id2meta[idx]
            results.append({
                "score": float(dist),
                "filename": meta["filename"],
                "chunk": meta["chunk"]
            })
        return results
