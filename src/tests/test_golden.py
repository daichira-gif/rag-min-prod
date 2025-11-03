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
def test_golden_retrieval():
    """
    Tests the retrieval pipeline against a "golden" expected output.
    This ensures that changes to embedding models or retrieval logic
    do not unexpectedly alter the top search result for a key query.
    """
    s = Settings()
    # Use the CI-specific model for consistency
    s.EMBEDDER_PROVIDER = "sentence_transformers"
    conn = None
    try:
        conn = psycopg2.connect(
            host=s.PGHOST,
            port=s.PGPORT,
            dbname=s.PGDATABASE,
            user=s.PGUSER,
            password=s.PGPASSWORD,
        )
        conn.autocommit = True

        store = VectorStore(conn)
        emb = Embedder.from_settings(s)
        retr = Retriever(conn, s)

        # Ensure the table is clean for a predictable test
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE documents RESTART IDENTITY;")

        # 1. Ingest known data
        content_gemini = "Gemini is a large language model created by Google."
        content_tokyo = "The capital of Japan is Tokyo."
        
        vec_gemini = emb.embed(content_gemini)
        doc_id_gemini = store.upsert_document(content_gemini, {"source":"golden-test"}, vec_gemini)

        vec_tokyo = emb.embed(content_tokyo)
        store.upsert_document(content_tokyo, {"source":"golden-test"}, vec_tokyo)

        # 2. Run a known query
        query = "Who made the Gemini model?"
        results = retr.retrieve(query, k=3)

        # 3. Assert against the "golden" expected result
        assert len(results) > 0, "Search returned no results"
        
        top_result_id = results[0][0]
        top_result_content = results[0][2]

        # The most relevant document ID should be the one for the Gemini content
        assert top_result_id == doc_id_gemini
        
        # The content should match exactly
        assert top_result_content == content_gemini

    finally:
        if conn:
            conn.close()
