# Minimal Production RAG (FastAPI + pgvector) — Starter

This is a minimal-but-production-minded RAG template with:
- **FastAPI** app (`src/app.py`)
- **Vector store**: PostgreSQL + **pgvector**
- **Docker** & **docker-compose**
- **CI/CD** (GitHub Actions): lint → test → build & push image → release
- **Evals**: `pytest` + simple **regression tests**
- **Observability**: OpenTelemetry (optional), structured logs, basic metrics
- **A/B testing** scaffolding for prompts/models
- **Security/Governance**: PII masking, prompt-injection tests, retention knobs

## Quickstart

This guide will get you up and running.

**1. Get the code**

Clone the repository to your local machine.
```bash
git clone https://github.com/daichira-gif/rag-min-prod.git
cd rag-min-prod
```

**2. Configure Environment**

Copy the sample environment file to a new `.env` file.
```bash
cp .env.sample .env
```
Now, open the `.env` file and fill in the required values.
> **Important:** The default setup uses OpenAI for embeddings. You **must** provide a valid `OPENAI_API_KEY`.

**3. Launch Services**

Build and launch the application and database containers in the background.
```bash
docker compose up --build -d
```

**4. Initialize Database**

The first time you launch the services, you need to initialize the database schema.
```bash
docker compose exec db psql -U rag -d rag -f /docker-entrypoint-initdb.d/init_db.sql
```

**5. Check Health**

Verify that the application is running correctly by checking the health endpoint.
```bash
curl http://localhost:8000/health
```
You should see `{"status":"ok"}`.

## Usage & Feature Testing

Once the application is running, you can test its features via the API.

### 1. Ingesting Data

To add a document to the vector database, send a POST request to the `/ingest` endpoint.

```bash
curl -X POST "http://localhost:8000/ingest" \
  -H "Content-Type: application/json" \
  -d '''{"content":"Gemini is a large language model created by Google."}'''
```

### 2. Querying

To ask a question, send a POST request to the `/query` endpoint. The system will find relevant documents and use them to generate an answer.

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '''{"query":"Who created Gemini?"}'''
```

> **Note for Windows PowerShell users:**
> `curl` is an alias for `Invoke-WebRequest` in PowerShell and has a different syntax. Use this format instead:
> ```powershell
> curl -Method POST -Uri "http://localhost:8000/query" -Headers @{ "Content-Type" = "application/json" } -Body '''{"query":"Who created Gemini?"}'''
> ```

### 3. Running Automated Tests

This project comes with a suite of automated tests. To run them, execute `pytest` inside the `app` container. You must set the `PYTHONPATH` for the tests to find the source code.

```bash
docker compose exec -e PYTHONPATH=. app pytest -v
```

### 4. A/B Testing

You can simulate different users to test the A/B bucketing logic by providing an `x-user-id` header in your query. The response will be prefixed with `[A]` or `[B]` depending on the calculated bucket.

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -H "x-user-id: user-123" \
  -d '''{"query":"What is this project?"}'''
```

## CI/CD

This repository is configured with GitHub Actions for CI/CD:
- **CI (`ci.yml`):** Automatically runs linting and tests on every push to the `main` branch or on any pull request. This ensures code quality and prevents regressions.
- **Release (`release.yml`):** When a Git tag matching the pattern `v*.*.*` (e.g., `v0.1.0`) is pushed, this workflow automatically builds a versioned Docker image, pushes it to GitHub Packages, and creates a corresponding GitHub Release.

## Notes

- The default embedding dimension is **1536** (for OpenAI `text-embedding-3-small`). If you switch to a different model (e.g., a 384-dimension MiniLM model) in your `.env` file, remember to also adjust the `embedding vector(1536)` line in `scripts/init_db.sql` to match.
- OpenTelemetry tracing is opt-in. To enable it, set the `OTEL_EXPORTER_OTLP_ENDPOINT` in your `.env` file to point to a collector (e.g., Jaeger, Datadog).