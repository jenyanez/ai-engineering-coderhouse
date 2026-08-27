"""Script de ingesta, chunking y generación de embeddings para ChromaDB."""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[1] / "pre_entrega_05" / ".env")

DOCS_DIR = Path(__file__).resolve().parent / "data" / "knowledge_documents"
CHROMA_DIR = Path(__file__).resolve().parent / "data" / "chroma_db"
COLLECTION_NAME = "multiagent_knowledge_base"


def load_documents() -> list[Document]:
    """Carga los documentos markdown de la base de conocimiento."""
    docs = []
    if not DOCS_DIR.exists():
        print(f"⚠️ Directorio {DOCS_DIR} no encontrado.")
        return docs

    for file_path in DOCS_DIR.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
            docs.append(Document(
                page_content=content,
                metadata={"source": file_path.name, "topic": file_path.stem}
            ))
    return docs


def run_ingestion():
    """Ejecuta el pipeline de chunking, embedding e indexación en ChromaDB."""
    print("=" * 70)
    print("🚀 INICIANDO INGESTA Y GENERACIÓN DE EMBEDDINGS EN CHROMADB")
    print("=" * 70)
    
    docs = load_documents()
    print(f"📄 Documentos fuente cargados: {len(docs)}")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n## ", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"🧩 Fragmentos (chunks) generados: {len(chunks)}")
    
    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
    )
    
    os.makedirs(CHROMA_DIR, exist_ok=True)
    
    print(f"💾 Guardando vectores en ChromaDB: {CHROMA_DIR}...")
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name=COLLECTION_NAME
    )
    
    print(f"✅ Ingesta completada con éxito. Colección: '{COLLECTION_NAME}'")
    print("=" * 70)
    return vectorstore


if __name__ == "__main__":
    run_ingestion()
