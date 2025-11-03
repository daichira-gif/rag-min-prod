CREATE EXTENSION IF NOT EXISTS vector;

-- Adjust 1536 to match your embedding dimension if needed
DROP TABLE IF EXISTS documents CASCADE;
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  embedding vector(384)
);

-- ivfflat index (requires ANALYZE, and best with suitable lists)
DROP INDEX IF EXISTS idx_documents_embedding;
CREATE INDEX idx_documents_embedding ON documents USING ivfflat (embedding vector_cosine_ops) WITH (lists = 100);

ANALYZE documents;
