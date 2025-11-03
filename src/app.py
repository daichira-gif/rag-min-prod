from __future__ import annotations
import os, json, psycopg2
from fastapi import FastAPI, Request, Header, Depends
from pydantic import BaseModel
from typing import Optional, Dict, Any
from .rag.config import Settings
from .rag.observability import setup_logging, setup_tracing_if_enabled
from .rag.pii import scrub
from .rag.retriever import Retriever
from .rag.abtest import bucket_for_user
from .rag.security import is_potential_injection
from .rag.embeddings import Embedder
from .rag.store import VectorStore
from prometheus_fastapi_instrumentator import Instrumentator

s = Settings()
setup_logging(level=s.LOG_LEVEL, mask_pii=s.MASK_PII_IN_LOGS)
setup_tracing_if_enabled(s)

app = FastAPI(title="Minimal Production RAG")

Instrumentator().instrument(app).expose(app, include_in_schema=False)

# Dependency to manage DB connections
def get_conn():
    conn = psycopg2.connect(
        host=s.PGHOST,
        port=s.PGPORT,
        dbname=s.PGDATABASE,
        user=s.PGUSER,
        password=s.PGPASSWORD,
    )
    conn.autocommit = True
    try:
        yield conn
    finally:
        conn.close()

class IngestReq(BaseModel):
    content: str
    metadata: Dict[str, Any] = {}

class QueryReq(BaseModel):
    query: str
    top_k: int = 3

@app.get("/health")
def health():
    return {"status":"ok"}

@app.post("/ingest")
def ingest(req: IngestReq, conn: Any = Depends(get_conn)):
    emb = Embedder.from_settings(s)
    store = VectorStore(conn)
    vec = emb.embed(req.content)
    _id = store.upsert_document(req.content, req.metadata, vec)
    return {"id": _id}

@app.post("/query")
def query(req: QueryReq, conn: Any = Depends(get_conn), x_user_id: Optional[str] = Header(default="")):
    # Security: basic prompt injection screening
    flag, phrase = is_potential_injection(req.query)
    if flag:
        return {"error": "Potential prompt injection detected", "phrase": phrase}

    # A/B bucket
    bucket = bucket_for_user(x_user_id or "anon", s.AB_DEFAULT_BUCKET)
    prompt_file = s.PROMPT_VERSION_A if bucket=="A" else s.PROMPT_VERSION_B
    try:
        with open(f"src/rag/prompts/{prompt_file}", "r", encoding="utf-8") as f:
            system_prompt = f.read().strip()
    except Exception:
        system_prompt = "Answer using retrieved context only."

    # Create retriever on-the-fly with the request-specific connection
    retriever = Retriever(conn, s)
    
    results = retriever.retrieve(req.query, k=req.top_k)
    context = "\n\n".join([r[2] for r in results])

    answer = f"[{bucket}] {system_prompt}\n\nContext:\n{context}\n\nQ: {req.query}\nA:"

    # Scrub logs for PII
    to_log = req.query
    if s.MASK_PII_IN_LOGS:
        to_log = scrub(to_log)
    print(json.dumps({"event":"query", "bucket":bucket, "query":to_log}))

    return {"answer": answer, "sources": [{"id": r[0], "score": r[1]} for r in results]}
