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

## Architecture Overview

This diagram shows the request flow for a `/query` request.

```text
+-------+      1. /query     +---------------------+      3. Embed Query     +------------------+
| User  | -----------------> | FastAPI Application | ----------------------> |   Embedding      |
+-------+                  | (Docker Container)  |                         | (OpenAI/Local)   |
                           +---------------------+                         +------------------+
                                 ^      |
                           8.     |      | 4. Vector Search
                        Response  |      v
                                  |  +---------------------+
                                  |  | VectorStore         |
                                  |  +---------------------+
                                  |            | 5. SQL Query
                                  |            v
                                  +->[PostgreSQL/pgvector]
                                       (Docker Container)
```

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

To ask a question, send a POST request to the `/query` endpoint.

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '''{"query":"Who created Gemini?"}'''
```

> **Note for Windows PowerShell users:**
> `curl` is an alias for `Invoke-WebRequest` in PowerShell and has a different syntax. For API testing, `Invoke-RestMethod` is often more convenient. Use this format:
> ```powershell
> Invoke-RestMethod -Uri http://localhost:8000/query -Method Post -Headers @{ "Content-Type" = "application/json" } -Body '''{"query":"Who created Gemini?"}'''
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

### 5. Interactive API Docs (Swagger UI)

FastAPI automatically generates interactive API documentation. While the application is running, navigate to [http://localhost:8000/docs](http://localhost:8000/docs) in your browser. This UI allows you to see all available endpoints and test them directly from your browser.

### 6. Testing Observability (OpenTelemetry + Jaeger)

This project is configured to send trace data using OpenTelemetry. You can visualize these traces locally using Jaeger.

1.  **Start Jaeger:** Run the all-in-one Jaeger container in a separate terminal.
    ```bash
    docker run -d --name jaeger \
      -e COLLECTOR_OTLP_ENABLED=true \
      -p 16686:16686 \
      -p 4317:4317 \
      jaegertracing/all-in-one:latest
    ```
2.  **Configure `.env`:** Set the OTel endpoint in your `.env` file.
    ```
    OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4317
    ```
3.  **Restart the App:** `docker compose restart app`
4.  **Send a Query:** Make a request to the `/query` endpoint.
5.  **View Traces:** Open the Jaeger UI at [http://localhost:16686](http://localhost:16686) in your browser. Select the `rag-min-prod` service to see the detailed trace of your request.

## Configuration (Environment Variables)

All configuration is managed via environment variables in the `.env` file.

| Variable                      | Description                                                              | Default Value                               |
| ----------------------------- | ------------------------------------------------------------------------ | ------------------------------------------- |
| `APP_ENV`                     | The application environment (e.g., `dev`, `prod`).                       | `dev`                                       |
| `HOST`                        | The host address for the app to listen on.                               | `0.0.0.0`                                   |
| `PORT`                        | The port for the app to listen on.                                       | `8000`                                      |
| `PGHOST`                      | Hostname of the PostgreSQL database.                                     | `db`                                        |
| `PGPORT`                      | Port of the PostgreSQL database.                                         | `5432`                                      |
| `PGDATABASE`                  | The name of the database to use.                                         | `rag`                                       |
| `PGUSER`                      | Username for the database connection.                                    | `rag`                                       |
| `PGPASSWORD`                  | Password for the database connection.                                    | `ragpassword`                               |
| `EMBED_DIM`                   | The dimension of the vectors. **Must match the model being used.**       | `1536`                                      |
| `EMBEDDER_PROVIDER`           | The embedding provider to use (`openai` or `sentence_transformers`).     | `openai`                                    |
| `OPENAI_API_KEY`              | Your OpenAI API key. Required if provider is `openai`.                   | `None`                                      |
| `SENTENCE_TRANSFORMERS_MODEL` | The specific Sentence Transformers model to use.                         | `sentence-transformers/all-MiniLM-L6-v2`    |
| `AB_DEFAULT_BUCKET`           | The default bucket (`A` or `B`) for A/B testing if a user cannot be bucketed. | `A`                                         |
| `PROMPT_VERSION_A`            | The filename of the prompt for bucket A.                                 | `prompt_v1.txt`                             |
| `PROMPT_VERSION_B`            | The filename of the prompt for bucket B.                                 | `prompt_v2.txt`                             |
| `MODEL_VERSION_A`             | The model version for bucket A.                                          | `gpt-4o-mini`                               |
| `MODEL_VERSION_B`             | The model version for bucket B.                                          | `gpt-4.1-mini`                              |
| `OTEL_EXPORTER_OTLP_ENDPOINT` | The endpoint for the OpenTelemetry collector. Leave empty to disable.    | `None`                                      |
| `LOG_LEVEL`                   | The logging level for the application.                                   | `INFO`                                      |
| `RETENTION_DAYS`              | Defines the intended data retention period in days. (See note below).    | `30`                                        |
| `MASK_PII_IN_LOGS`            | If `true`, masks Personally Identifiable Information (PII) in logs.        | `True`                                      |
| `ALLOW_PROMPT_INJECTION_TESTS`| A flag used by security tests.                                           | `True`                                      |

## CI/CD

This repository is configured with GitHub Actions for CI/CD:
- **CI (`ci.yml`):** Automatically runs linting and tests on every push to the `main` branch or on any pull request. This ensures code quality and prevents regressions.
- **Release (`release.yml`):** When a Git tag matching the pattern `v*.*.*` (e.g., `v0.1.0`) is pushed, this workflow automatically builds a versioned Docker image, pushes it to GitHub Packages, and creates a corresponding GitHub Release.

## Future Enhancements

This project provides a solid foundation. Here are some potential next steps to make it even more robust:

- **Database Migrations (Alembic):** Currently, the database schema is managed by a single `init_db.sql` file. For team-based development or more complex schema changes over time, introducing a migration tool like [Alembic](https://alembic.sqlalchemy.org/) is highly recommended. This allows for version-controlled, repeatable, and reversible changes to the database structure.

## Notes

- **Embedding Dimension**: The default embedding dimension is **1536** (for OpenAI `text-embedding-3-small`). If you switch to a different model (e.g., a 384-dimension MiniLM model) in your `.env` file, remember to also adjust the `embedding vector(1536)` line in `scripts/init_db.sql` to match.

- **OpenTelemetry**: Tracing is opt-in. To enable it, set the `OTEL_EXPORTER_OTLP_ENDPOINT` in your `.env` file to point to a collector (e.g., Jaeger, Datadog).

- **Data Retention Policy**: The `.env` file includes a `RETENTION_DAYS` setting, which is intended to define a data retention policy. Please note that the logic for automatically deleting documents older than this specified period **is not yet implemented** in the current version of this project. A future improvement would be to add a scheduled background task that periodically removes old documents from the database.