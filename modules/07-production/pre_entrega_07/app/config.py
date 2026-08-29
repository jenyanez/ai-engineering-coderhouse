"""Configuración centralizada de variables de entorno y parámetros de producción."""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno desde la raíz del proyecto
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")
load_dotenv(BASE_DIR.parent / "pre_entrega_06" / ".env")
load_dotenv(BASE_DIR.parent / "pre_entrega_05" / ".env")


class Settings:
    """Parámetros de configuración del sistema."""

    # API Server
    API_TITLE: str = "Multi-Agent Production API"
    API_VERSION: str = "1.0.0"
    API_DESCRIPTION: str = "API asíncrona de orquestación multi-agente con Redis, Phoenix y HITL"
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_URL: str = os.getenv("REDIS_URL", f"redis://{REDIS_HOST}:{REDIS_PORT}/{REDIS_DB}")
    JOB_TTL_SECONDS: int = int(os.getenv("JOB_TTL_SECONDS", "86400"))  # 24 horas

    # Arize Phoenix / OpenTelemetry
    PHOENIX_HOST: str = os.getenv("PHOENIX_HOST", "127.0.0.1")
    PHOENIX_PORT: int = int(os.getenv("PHOENIX_PORT", "6006"))
    PHOENIX_COLLECTOR_ENDPOINT: str = os.getenv(
        "PHOENIX_COLLECTOR_ENDPOINT", f"http://{PHOENIX_HOST}:{PHOENIX_PORT}/v1/traces"
    )
    PHOENIX_PROJECT_NAME: str = os.getenv("PHOENIX_PROJECT_NAME", "pre_entrega_07")

    # OpenAI & LLM Models
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
    OPENAI_EMBEDDINGS_MODEL: str = os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")

    # Rutas del Sistema
    DATA_DIR: Path = BASE_DIR / "data"
    CHROMA_DIR: Path = DATA_DIR / "chroma_db"
    COLLECTION_NAME: str = "multiagent_knowledge_base"


settings = Settings()
