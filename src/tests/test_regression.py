import os
import pytest
import psycopg2
from src.rag.config import Settings
from src.rag.embeddings import Embedder
from src.rag.store import VectorStore
from src.rag.retriever import Retriever

requires_db = pytest.mark.skipif(
    os.environ.get("PGHOST") is None, reason="DB not available in env"
)

@requires_db
def test_retrieval_pipeline_smoke():
    s = Settings()
    conn = None
    try:
        # 1. Create DB connection for the test
        conn = psycopg2.connect(
            host=s.PGHOST,
            port=s.PGPORT,
            dbname=s.PGDATABASE,
            user=s.PGUSER,
            password=s.PGPASSWORD,
        )
        conn.autocommit = True

        # 2. Instantiate classes with the connection
        store = VectorStore(conn)
        emb = Embedder.from_settings(s)
        retr = Retriever(conn, s)

        # 3. Run the test logic
        content = "RAG template uses FastAPI and pgvector."
        vec = emb.embed(content)
        doc_id = store.upsert_document(content, {"test":"true"}, vec)
        results = retr.retrieve("pgvector", k=3)
        assert any(r[0] == doc_id for r in results)

    finally:
        # 4. Ensure connection is closed
        if conn:
            conn.close()
