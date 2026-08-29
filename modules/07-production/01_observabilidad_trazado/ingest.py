"""Pipeline de ingesta, chunking y generación de embeddings para ChromaDB."""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

# Cargar entorno
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / "pre_entrega_06" / ".env")

DOCS_DIR = Path(__file__).resolve().parent / "data" / "knowledge_documents"
CHROMA_DIR = Path(__file__).resolve().parent / "data" / "chroma_db"
COLLECTION_NAME = "modulo7_observability_kb"


def load_documents() -> list[Document]:
    """Carga los documentos Markdown de la base de conocimiento."""
    docs = []
    if not DOCS_DIR.exists():
        return docs
    for file_path in DOCS_DIR.glob("*.md"):
        with open(file_path, "r", encoding="utf-8") as f:
            docs.append(Document(
                page_content=f.read(),
                metadata={"source": file_path.name, "topic": file_path.stem}
            ))
    return docs


def run_ingestion():
    """Ejecuta el chunking y generación de embeddings en ChromaDB."""
    print("=" * 70)
    print("🚀 INGESTANDO DOCUMENTOS EN CHROMADB PARA MÓDULO 7")
    print("=" * 70)
    
    docs = load_documents()
    print(f"📄 Documentos cargados: {len(docs)}")
    
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=400,
        chunk_overlap=50,
        separators=["\n## ", "\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    print(f"🧩 Fragmentos generados: {len(chunks)}")
    
    embeddings = OpenAIEmbeddings(
        model=os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
    )
    
    os.makedirs(CHROMA_DIR, exist_ok=True)
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=str(CHROMA_DIR),
        collection_name=COLLECTION_NAME
    )
    print(f"✅ Ingesta completada con éxito en: {CHROMA_DIR}")
    print("=" * 70)
    return vectorstore


if __name__ == "__main__":
    run_ingestion()
