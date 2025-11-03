from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    APP_ENV: str = "dev"
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    PGHOST: str = "localhost"
    PGPORT: int = 5432
    PGDATABASE: str = "rag"
    PGUSER: str = "rag"
    PGPASSWORD: str = "ragpassword"
    EMBED_DIM: int = 1536

    EMBEDDER_PROVIDER: str = "openai"   # openai | sentence_transformers
    OPENAI_API_KEY: str | None = None
    SENTENCE_TRANSFORMERS_MODEL: str = "sentence-transformers/all-MiniLM-L6-v2"

    AB_DEFAULT_BUCKET: str = "A"
    PROMPT_VERSION_A: str = "prompt_v1.txt"
    PROMPT_VERSION_B: str = "prompt_v2.txt"
    MODEL_VERSION_A: str = "gpt-4o-mini"
    MODEL_VERSION_B: str = "gpt-4.1-mini"

    OTEL_EXPORTER_OTLP_ENDPOINT: str | None = None
    LOG_LEVEL: str = "INFO"
    RETENTION_DAYS: int = 30

    MASK_PII_IN_LOGS: bool = True
    ALLOW_PROMPT_INJECTION_TESTS: bool = True

    class Config:
        env_file = ".env"
        extra = "ignore"
