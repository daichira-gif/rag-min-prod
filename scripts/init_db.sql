CREATE EXTENSION IF NOT EXISTS vector;

-- Adjust 1536 to match your embedding dimension if needed
DROP TABLE IF EXISTS documents CASCADE;
CREATE TABLE documents (
  id SERIAL PRIMARY KEY,
  content TEXT NOT NULL,
  metadata JSONB DEFAULT '{}'::jsonb,
  embedding vector(1536)
);

