"""
config.py — Configuración e Infraestructura Cloud (Pinecone Serverless).

Responsabilidades:
- Cargar variables de entorno desde .env.
- Inicializar el cliente de Pinecone.
- Verificar/crear el índice Serverless de forma idempotente.
"""

import os
import time

from dotenv import load_dotenv
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

# --- Variables de Entorno ---
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
INDEX_NAME = os.getenv("INDEX_NAME", "pre-entrega-04")

# --- Constantes del Proyecto ---
EMBEDDING_MODEL = "text-embedding-3-small"
EMBEDDING_DIMENSION = 1536
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
NAMESPACE = "documentos"


def get_pinecone_client() -> Pinecone:
    """Inicializa y retorna el cliente de Pinecone."""
    if not PINECONE_API_KEY:
        raise ValueError(
            "❌ PINECONE_API_KEY no encontrada en .env. "
            "Copia .env.example a .env y agrega tus credenciales."
        )
    return Pinecone(api_key=PINECONE_API_KEY)


def setup_index() -> None:
    """
    Verifica si el índice existe en Pinecone y lo crea si es necesario.
    Operación idempotente: espera activa hasta que el índice esté 'ready'.
    """
    pc = get_pinecone_client()
    existing = [idx.name for idx in pc.list_indexes()]

    if INDEX_NAME not in existing:
        print(f"🛠️ Creando índice '{INDEX_NAME}' (dim={EMBEDDING_DIMENSION}, metric=cosine)...")
        pc.create_index(
            name=INDEX_NAME,
            dimension=EMBEDDING_DIMENSION,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1"),
        )
        # Espera activa hasta que esté listo
        while not pc.describe_index(INDEX_NAME).status["ready"]:
            print("⏳ Esperando a que el índice de Pinecone esté listo...")
            time.sleep(2)
        print(f"✅ Índice '{INDEX_NAME}' creado y listo para su uso.")
    else:
        print(f"ℹ️ Índice '{INDEX_NAME}' ya existe y está activo.")


if __name__ == "__main__":
    setup_index()
