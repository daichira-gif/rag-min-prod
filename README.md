# Minimal Production RAG (FastAPI + pgvector) — Starter

This is a minimal-but-production-minded RAG template with:
- **FastAPI** app (`src/app.py`)
- **Vector store**: PostgreSQL + **pgvector**
- **Docker** & **docker-compose**
- **CI/CD** (GitHub Actions): lint → test → (optionally) build & push image → release
- **Evals**: `pytest` + simple **regression tests**
- **Observability**: OpenTelemetry (optional), structured logs, basic metrics
- **A/B testing** scaffolding for prompts/models
- **Security/Governance**: PII masking, prompt-injection tests, retention knobs

## Quickstart

1. Copy `.env.sample` to `.env` and set values (OpenAI key, DB, etc.).
2. Launch services:
   ```bash
   docker compose up --build
   ```
3. Initialize DB schema:
   ```bash
   docker compose exec db psql -U rag -d rag -f /docker-entrypoint-initdb.d/init_db.sql
   ```
4. (Optional) Seed sample docs:
   ```bash
   docker compose exec app python -m scripts.seed
   ```
5. Try it:
   ```bash
   curl -X POST "http://localhost:8000/query" -H "Content-Type: application/json"      -d '{"query":"What is this project?"}'
   ```

## Project layout

```text
rag-min-prod/
  .env.sample
  docker-compose.yml
  Dockerfile
  requirements.txt
  requirements-dev.txt
  src/
    app.py
    rag/
      __init__.py
      config.py
      embeddings.py
      store.py
      retriever.py
      evaluator.py
      pii.py
      observability.py
      abtest.py
      security.py
      prompts/
        prompt_v1.txt
        prompt_v2.txt
    tests/
      test_smoke.py
      test_regression.py
      test_prompt_injection.py
  scripts/
    init_db.sql
    seed.py
    bench.py
  .github/workflows/ci.yml
  .github/workflows/release.yml
```

## Notes

- Default embedding dim is **1536** (OpenAI `text-embedding-3-small`). If you use local models (e.g. 384-dim MiniLM), adjust `scripts/init_db.sql` and `EMBED_DIM` in `.env`.
- OpenTelemetry is **opt-in**. Set `OTEL_EXPORTER_OTLP_ENDPOINT` to enable.
- Regression tests require the DB; CI spins a pgvector service.
- See `SECURITY.md` inside README section below for governance choices.
