"""Módulo de configuración centralizada del sistema Intelligence."""

import os
from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Configuración inmutable y tipada mediante Pydantic Settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # Configuración de servidor
    host: str = Field(default="0.0.0.0", alias="HOST")
    port: int = Field(default=8000, alias="PORT")
    environment: str = Field(default="production", alias="ENVIRONMENT")

    # Proveedor LLM y Embeddings
    openai_api_key: str = Field(default="", alias="OPENAI_API_KEY")
    openai_model: str = Field(default="gpt-4o-mini", alias="OPENAI_MODEL")
    openai_embedding_model: str = Field(
        default="text-embedding-3-small", alias="OPENAI_EMBEDDING_MODEL"
    )

    # Infraestructura Redis
    redis_url: str = Field(default="redis://localhost:6379/0", alias="REDIS_URL")
    redis_queue_name: str = Field(
        default="intelligence_tasks_queue", alias="REDIS_QUEUE_NAME"
    )
    redis_status_prefix: str = Field(
        default="intelligence_status:", alias="REDIS_STATUS_PREFIX"
    )
    redis_checkpoint_prefix: str = Field(
        default="intelligence_checkpoint:", alias="REDIS_CHECKPOINT_PREFIX"
    )

    # Observabilidad Arize Phoenix
    phoenix_collector_endpoint: str = Field(
        default="http://localhost:6006/v1/traces",
        alias="PHOENIX_COLLECTOR_ENDPOINT",
    )
    phoenix_project_name: str = Field(
        default="intelligence-production-system",
        alias="PHOENIX_PROJECT_NAME",
    )

    # Base de datos vectorial persistente ChromaDB
    chroma_persist_directory: str = Field(
        default="data/chroma_db", alias="CHROMA_PERSIST_DIRECTORY"
    )
    chroma_collection_name: str = Field(
        default="intelligence_knowledge_base",
        alias="CHROMA_COLLECTION_NAME",
    )


settings = Settings()
