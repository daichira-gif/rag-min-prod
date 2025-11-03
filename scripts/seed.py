from src.rag.config import Settings
from src.rag.embeddings import Embedder
from src.rag.store import VectorStore

def main():
    s = Settings()
    store = VectorStore.from_settings(s)
    emb = Embedder.from_settings(s)

    docs = [
        {"content": "This repository is a minimal production-ready RAG template using FastAPI and pgvector.", "metadata": {"source":"seed"}},
        {"content": "It includes CI/CD, observability with OpenTelemetry, and security features like PII masking.", "metadata": {"source":"seed"}},
        {"content": "A/B testing scaffolding allows comparing two prompt/model setups safely.", "metadata": {"source":"seed"}},
    ]
    for d in docs:
        vec = emb.embed(d["content"])
        store.upsert_document(d["content"], d.get("metadata", {}), vec)
    print("Seeded {} docs.".format(len(docs)))

if __name__ == "__main__":
    main()
