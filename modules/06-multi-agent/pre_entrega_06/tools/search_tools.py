"""Herramientas de búsqueda y consulta semántica sobre ChromaDB para el Agente de Investigación."""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_chroma import Chroma
from langchain_core.tools import tool
from langchain_openai import OpenAIEmbeddings

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent.parent / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / "pre_entrega_05" / ".env")

CHROMA_DIR = Path(__file__).resolve().parent.parent / "data" / "chroma_db"
COLLECTION_NAME = "multiagent_knowledge_base"


def get_chroma_retriever():
    """Inicializa la conexión con el VectorStore de ChromaDB persistente."""
    if not CHROMA_DIR.exists():
        return None
    try:
        embeddings = OpenAIEmbeddings(
            model=os.getenv("OPENAI_EMBEDDINGS_MODEL", "text-embedding-3-small")
        )
        return Chroma(
            persist_directory=str(CHROMA_DIR),
            collection_name=COLLECTION_NAME,
            embedding_function=embeddings
        )
    except Exception:
        return None


@tool
def query_chroma_vector_db(query: str, k: int = 3) -> str:
    """Realiza una búsqueda semántica por similitud de cosenos en la Vector Database ChromaDB.
    
    Args:
        query: Pregunta o concepto técnico/mercado a buscar en los documentos indexados.
        k: Número de fragmentos más relevantes a recuperar (default: 3).
    """
    vectorstore = get_chroma_retriever()
    if not vectorstore:
        return json.dumps({
            "status": "warning",
            "message": "ChromaDB no inicializado localmente. Ejecutar ingest.py."
        }, ensure_ascii=False)
        
    try:
        results = vectorstore.similarity_search_with_relevance_scores(query, k=k)
        retrieved_chunks = []
        for doc, score in results:
            retrieved_chunks.append({
                "content": doc.page_content,
                "source": doc.metadata.get("source", "documento_tecnico.md"),
                "relevance_score": round(float(score), 4)
            })
            
        return json.dumps({
            "status": "success",
            "query": query,
            "total_retrieved": len(retrieved_chunks),
            "chunks": retrieved_chunks
        }, ensure_ascii=False)
    except Exception as exc:
        return json.dumps({"error": f"Error consultando ChromaDB: {str(exc)}"}, ensure_ascii=False)


@tool
def search_market_trends(query: str) -> str:
    """Busca datos de mercado, tamaño de industria y proyecciones en la base vectorial ChromaDB.
    
    Args:
        query: Término de búsqueda o tecnología (ej. 'IA generativa', 'sistemas multi-agente', 'RAG avanzado').
    """
    # Consulta semántica en la Vector DB
    res = query_chroma_vector_db.invoke({"query": query, "k": 2})
    return res


@tool
def query_tech_knowledge_base(topic: str) -> str:
    """Consulta en ChromaDB mejores prácticas de ingeniería, drivers y riesgos técnicos.
    
    Args:
        topic: Concepto técnico o arquitectura a consultar.
    """
    res = query_chroma_vector_db.invoke({"query": f"factores impulsores riesgos {topic}", "k": 2})
    return res
