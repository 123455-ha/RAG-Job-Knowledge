from functools import lru_cache
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "RAG Job Knowledge Assistant"
    app_env: str = "development"
    openai_api_key: str = ""
    openai_base_url: str = ""
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    embedding_api_key: str = ""
    embedding_base_url: str = ""
    qdrant_url: str = "http://localhost:6333"
    qdrant_collection: str = "job_knowledge"
    chunk_size: int = 500
    chunk_overlap: int = 100
    top_k: int = 5
    max_file_size_mb: int = 20
    database_url: str = "sqlite:///./data/rag.db"
    upload_dir: str = "./data/uploads"

    model_config = SettingsConfigDict(env_file=".env", env_prefix="", extra="ignore")

    @property
    def database_path(self) -> Path:
        return Path(self.database_url.replace("sqlite:///", ""))


@lru_cache
def get_settings() -> Settings:
    settings = Settings()
    Path(settings.upload_dir).mkdir(parents=True, exist_ok=True)
    settings.database_path.parent.mkdir(parents=True, exist_ok=True)
    return settings
