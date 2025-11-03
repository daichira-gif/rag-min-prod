from __future__ import annotations
from typing import List
from .config import Settings

class Embedder:
    def __init__(self, settings: Settings):
        self.s = settings
        if self.s.EMBEDDER_PROVIDER == "openai":
            from openai import OpenAI
            if not self.s.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set")
            self.client = OpenAI(api_key=self.s.OPENAI_API_KEY)
            self.model = "text-embedding-3-small"
            self.dim = 1536
        else:
            from sentence_transformers import SentenceTransformer
            self.model = self.s.SENTENCE_TRANSFORMERS_MODEL
            self.encoder = SentenceTransformer(self.model)
            # assume 384 for MiniLM; for generality we query model.get_sentence_embedding_dimension()
            self.dim = getattr(self.encoder, "get_sentence_embedding_dimension", lambda: 384)()

        if self.dim != self.s.EMBED_DIM:
            # Warn, but do not fail hard
            print(f"[Embedder] WARNING: model dim={self.dim} != configured EMBED_DIM={self.s.EMBED_DIM}")

    @classmethod
    def from_settings(cls, s: Settings) -> "Embedder":
        return cls(s)

    def embed(self, text: str) -> List[float]:
        if self.s.EMBEDDER_PROVIDER == "openai":
            r = self.client.embeddings.create(input=text, model=self.model)
            return r.data[0].embedding
        else:
            vec = self.encoder.encode([text], normalize_embeddings=True)[0]
            return vec.tolist()
