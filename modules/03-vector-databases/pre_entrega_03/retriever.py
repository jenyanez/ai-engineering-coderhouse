"""
retriever.py — Capa de Recuperación Semántica.

Responsabilidades:
- Crear el retriever a partir del vectorstore existente.
- Formatear documentos recuperados para inyectar en el prompt.
"""

from langchain_core.documents import Document
from langchain_core.vectorstores import VectorStoreRetriever
from langchain_chroma import Chroma

from ingesta import crear_embeddings, PERSIST_DIR, COLLECTION_NAME


# Cache global para evitar recargar el modelo de embeddings en cada consulta
_embeddings_instance = None


def obtener_embeddings_cached():
    global _embeddings_instance
    if _embeddings_instance is None:
        _embeddings_instance = crear_embeddings()
    return _embeddings_instance


def cargar_vectorstore() -> Chroma:
    """
    Carga el vectorstore persistente de ChromaDB.

    Usa el MISMO modelo de embeddings que se usó para indexar,
    garantizando coherencia en las distancias vectoriales.
    """
    embeddings = obtener_embeddings_cached()
    return Chroma(
        collection_name=COLLECTION_NAME,
        embedding_function=embeddings,
        persist_directory=PERSIST_DIR,
    )


def crear_retriever(vectorstore: Chroma | None = None) -> VectorStoreRetriever:
    """
    Crea un retriever con búsqueda por similitud.

    Args:
        vectorstore: Instancia de Chroma. Si no se pasa, carga el persistente.

    Returns:
        Retriever configurado con k=4 (entre 3 y 5, como pide la consigna).
    """
    if vectorstore is None:
        vectorstore = cargar_vectorstore()

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 4},
    )


def formatear_documentos(docs: list[Document]) -> str:
    """
    Convierte los documentos recuperados en un bloque de texto
    con etiquetas de fuente para inyectar en el prompt del LLM.

    Args:
        docs: Lista de Document con metadata['source'].

    Returns:
        String con fragmentos separados y etiquetados por fuente.
    """
    return "\n\n---\n\n".join(
        f"[Fuente: {d.metadata.get('source', 'desconocida')}]\n{d.page_content}"
        for d in docs
    )
