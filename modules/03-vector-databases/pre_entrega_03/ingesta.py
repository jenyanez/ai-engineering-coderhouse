"""
ingesta.py — Módulo de Ingesta: carga, chunking y persistencia en ChromaDB.

Responsabilidades:
- Cargar archivos .txt de la carpeta /data.
- Fragmentar con RecursiveCharacterTextSplitter (500 tokens, 50 overlap).
- Persistir en ChromaDB con chequeo anti-reindexado.
"""

import os

from langchain_community.document_loaders import DirectoryLoader, TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_huggingface import HuggingFaceEmbeddings

# --- Configuración ---
DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
PERSIST_DIR = os.path.join(os.path.dirname(__file__), "vectorstore")
COLLECTION_NAME = "ia_negocios"
EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


def crear_embeddings() -> HuggingFaceEmbeddings:
    """
    Instancia el modelo de embeddings.

    IMPORTANTE: se usa el MISMO modelo para indexar y consultar.
    Mezclar modelos distintos invalida las distancias vectoriales.
    """
    return HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)


def cargar_y_fragmentar() -> list:
    """
    Carga todos los .txt de /data y los fragmenta en chunks de 500 tokens.

    Returns:
        Lista de Document con metadata de fuente preservada.
    """
    loader = DirectoryLoader(
        DATA_DIR,
        glob="*.txt",
        loader_cls=TextLoader,
        loader_kwargs={"encoding": "utf-8"},
    )
    documentos_crudos = loader.load()
    print(f"📄 Documentos cargados: {len(documentos_crudos)}")

    # Chunking en tokens (no caracteres) — el límite del LLM se mide en tokens
    splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
        chunk_size=500,
        chunk_overlap=50,
    )
    chunks = splitter.split_documents(documentos_crudos)

    print(f"✂️  Fragmentos generados: {len(chunks)}")
    return chunks


def indexar_documentos() -> Chroma:
    """
    Carga documentos en ChromaDB con persistencia local.

    Si el índice ya existe, lo carga sin reindexar (optimización de tiempo y costo).
    Si no existe, fragmenta e indexa desde cero.

    Returns:
        Instancia de Chroma conectada a la colección.
    """
    embeddings = crear_embeddings()
    ya_existe = os.path.exists(PERSIST_DIR) and len(os.listdir(PERSIST_DIR)) > 0

    if ya_existe:
        vectorstore = Chroma(
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR,
        )
        if vectorstore._collection.count() == 0:
            print("⚠️  Índice vacío o corrupto detectado — re-indexando documentos")
            chunks = cargar_y_fragmentar()
            vectorstore = Chroma.from_documents(
                documents=chunks,
                embedding=embeddings,
                collection_name=COLLECTION_NAME,
                persist_directory=PERSIST_DIR,
            )
        else:
            print("♻️  Índice existente detectado — cargando sin reindexar")
    else:
        print("🆕 No hay índice previo — indexando documentos por primera vez")
        chunks = cargar_y_fragmentar()
        vectorstore = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            collection_name=COLLECTION_NAME,
            persist_directory=PERSIST_DIR,
        )

    cantidad = vectorstore._collection.count()
    print(f"📦 Documentos en la colección: {cantidad}")
    return vectorstore
