"""
ingesta.py — Pipeline de Ingesta: carga, chunking y persistencia en Pinecone.

Responsabilidades:
- Cargar archivos .txt de la carpeta /data.
- Fragmentar con RecursiveCharacterTextSplitter (~500 tokens, 50 overlap).
- Enriquecer metadatos (source, category, page, text).
- Subir a Pinecone Serverless en lotes con namespace.
"""

import hashlib
import json
import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from config import (
    DATA_DIR,
    EMBEDDING_MODEL,
    INDEX_NAME,
    NAMESPACE,
    OPENAI_API_KEY,
    setup_index,
)

HASH_RECORD_FILE = os.path.join(os.path.dirname(__file__), ".ingest_hashes.json")


def crear_embeddings() -> OpenAIEmbeddings:
    """Instancia el modelo de embeddings de OpenAI."""
    if not OPENAI_API_KEY:
        raise ValueError("❌ OPENAI_API_KEY no encontrada en .env.")
    return OpenAIEmbeddings(model=EMBEDDING_MODEL)


def calcular_hash_texto(texto: str) -> str:
    """Calcula el hash SHA-256 del contenido de un texto."""
    return hashlib.sha256(texto.encode("utf-8")).hexdigest()


def cargar_y_fragmentar() -> list:
    """
    Carga todos los .txt de /data y los fragmenta en chunks de ~500 tokens.

    Enriquece la metadata de cada chunk con:
    - source: nombre del archivo de origen.
    - category: categoría derivada del nombre del archivo.
    - page: número de fragmento dentro del corpus.
    - chunk_hash: hash SHA-256 único del contenido para control de cambios.
    - text: contenido completo del chunk (para evitar DB relacional adicional).
    """
    loader = DirectoryLoader(
        DATA_DIR,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documentos_crudos = loader.load()
    print(f"📄 Documentos cargados: {len(documentos_crudos)}")

    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_documents(documentos_crudos)

    # Enriquecer metadatos de cada chunk y sanitizar
    for idx, chunk in enumerate(chunks):
        nombre_archivo = os.path.basename(
            chunk.metadata.get("source") or "desconocido"
        )
        category = nombre_archivo.replace(".txt", "").replace("_", " ").title()
        c_hash = calcular_hash_texto(chunk.page_content)

        raw_metadata = {
            "source": str(nombre_archivo),
            "category": str(category),
            "page": int(idx),
            "chunk_hash": str(c_hash),
            "text": str(chunk.page_content),
        }
        # Sanitizar: filtrar cualquier clave con valor None
        chunk.metadata = {k: v for k, v in raw_metadata.items() if v is not None}

    print(f"✂️  Fragmentos generados y sanitizados: {len(chunks)}")
    return chunks


def indexar_documentos(force_reindex: bool = False) -> PineconeVectorStore:
    """
    Pipeline idempotente con hashes SHA-256:
    setup de índice → chequeo de cambios → chunking → embedding → upsert a Pinecone.
    """
    # 1. Verificar/crear el índice
    setup_index()

    chunks = cargar_y_fragmentar()
    hashes_actuales = [c.metadata["chunk_hash"] for c in chunks]

    # Chequeo idempotente de ingesta previa
    if os.path.exists(HASH_RECORD_FILE) and not force_reindex:
        try:
            with open(HASH_RECORD_FILE, "r", encoding="utf-8") as f:
                hashes_previos = json.load(f)
            if hashes_previos == hashes_actuales:
                print("♻️  Los documentos y hashes coinciden exactamente. Saltando ingesta (Idempotente).")
                embeddings = crear_embeddings()
                return PineconeVectorStore(
                    index_name=INDEX_NAME,
                    embedding=embeddings,
                    namespace=NAMESPACE,
                )
        except Exception:
            pass

    # 2. Generar embeddings y subir a Pinecone
    embeddings = crear_embeddings()
    print(f"📤 Subiendo {len(chunks)} chunks a Pinecone (namespace: '{NAMESPACE}')...")

    vectorstore = PineconeVectorStore.from_documents(
        documents=chunks,
        embedding=embeddings,
        index_name=INDEX_NAME,
        namespace=NAMESPACE,
    )

    # Guardar estado de hashes procesados
    with open(HASH_RECORD_FILE, "w", encoding="utf-8") as f:
        json.dump(hashes_actuales, f, indent=2)

    print("✅ Ingesta completada exitosamente (hashes guardados).")
    return vectorstore


if __name__ == "__main__":
    indexar_documentos()
