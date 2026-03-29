from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # AWS
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_region: str = "us-east-1"
    aws_session_token: str | None = None

    # Bedrock
    bedrock_embedding_model_id: str = "amazon.titan-embed-text-v2:0"
    bedrock_llm_model_id: str = "us.anthropic.claude-sonnet-4-20250514-v1:0"

    # PostgreSQL
    database_url: str

    # ChromaDB (local persistent path — no server needed)
    chroma_persist_dir: str = "./data/chroma"

    # JWT
    jwt_secret_key: str
    jwt_algorithm: str = "HS256"
    jwt_expire_minutes: int = 60

    # App
    app_env: str = "local"
    log_level: str = "INFO"

    model_config = SettingsConfigDict(env_file=".env", case_sensitive=False, extra="ignore")


@lru_cache
def get_settings() -> Settings:
    return Settings()
