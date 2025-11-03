from __future__ import annotations
from typing import List, Dict, Any
from .config import Settings
from .embeddings import Embedder
from .store import VectorStore

class Retriever:
    def __init__(self, conn: Any, settings: Settings):
        self.s = settings
        self.emb = Embedder.from_settings(settings)
        self.store = VectorStore(conn)

    def retrieve(self, query: str, k: int = 3):
        qvec = self.emb.embed(query)
        results = self.store.search(qvec, k=k)
        return results
