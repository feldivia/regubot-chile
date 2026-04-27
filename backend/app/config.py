"""Configuración centralizada de la aplicación."""

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Base de datos
    database_url: str = "postgresql+asyncpg://regbot:regbot@localhost:5432/regbot"

    # Redis
    redis_url: str = ""

    # API Keys
    anthropic_api_key: str = ""
    openai_api_key: str = ""

    # Banco Central
    bcch_user: str = ""
    bcch_password: str = ""

    # Modelos
    claude_model: str = "claude-haiku-4-5-20251001"
    embedding_model: str = "text-embedding-3-large"
    embedding_dimensions: int = 3072

    # Rate limiting
    rate_limit_per_min: int = 20

    # Observabilidad
    sentry_dsn: str = ""
    log_level: str = "INFO"

    # RAG
    retrieval_top_k: int = 10
    rerank_top_k: int = 5
    similarity_threshold: float = 0.7
    verification_threshold: float = 0.6

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8", "extra": "ignore"}


settings = Settings()
