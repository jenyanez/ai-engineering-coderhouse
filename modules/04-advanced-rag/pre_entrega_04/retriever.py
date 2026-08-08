"""
retriever.py — Recuperador Híbrido: BM25 + Pinecone Semántico.

Responsabilidades:
- Configurar PineconeVectorStore como retriever semántico.
- Cargar los chunks en BM25Retriever para búsqueda léxica.
- Combinar ambos con EnsembleRetriever.
"""

from langchain_community.retrievers import BM25Retriever
try:
    from langchain_classic.retrievers.ensemble import EnsembleRetriever
except ImportError:
    try:
        from langchain.retrievers import EnsembleRetriever
    except ImportError:
        from langchain_community.retrievers.ensemble import EnsembleRetriever
from langchain_core.documents import Document
from langchain_openai import OpenAIEmbeddings
from langchain_pinecone import PineconeVectorStore

from config import EMBEDDING_MODEL, INDEX_NAME, NAMESPACE


class RAGSystem:
    """
    Sistema RAG con recuperación híbrida.

    Combina búsqueda semántica (vectorial en Pinecone) con
    búsqueda léxica (BM25 en memoria) mediante EnsembleRetriever.
    """

    def __init__(self, chunks: list[Document], top_k: int = 5):
        """
        Args:
            chunks: Lista de Document (los mismos usados en la ingesta).
            top_k: Cantidad de documentos a recuperar por cada estrategia.
        """
        self.top_k = top_k
        self.chunks = chunks

        # Retriever semántico (Pinecone)
        embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
        vectorstore = PineconeVectorStore(
            index_name=INDEX_NAME,
            embedding=embeddings,
            namespace=NAMESPACE,
        )
        self.semantic_retriever = vectorstore.as_retriever(
            search_kwargs={"k": top_k},
        )

        # Retriever léxico (BM25 en memoria)
        self.bm25_retriever = BM25Retriever.from_documents(
            chunks, k=top_k,
        )

        # Retriever híbrido (Ensemble: 50% semántico + 50% léxico)
        self.ensemble_retriever = EnsembleRetriever(
            retrievers=[self.semantic_retriever, self.bm25_retriever],
            weights=[0.5, 0.5],
        )

    async def retrieve(
        self, query: str, filter_dict: dict | None = None
    ) -> list[Document]:
        """
        Ejecuta la recuperación híbrida y retorna los Top-K documentos combinados.

        Args:
            query: Texto de la consulta.
            filter_dict: Filtro de metadatos opcional para Pinecone (ej: {"category": "Estrategia Ia Ventas"}).
        """
        if filter_dict:
            # Búsqueda semántica filtrada directamente en Pinecone
            embeddings = OpenAIEmbeddings(model=EMBEDDING_MODEL)
            filtered_vectorstore = PineconeVectorStore(
                index_name=INDEX_NAME,
                embedding=embeddings,
                namespace=NAMESPACE,
            )
            filtered_retriever = filtered_vectorstore.as_retriever(
                search_kwargs={"k": self.top_k, "filter": filter_dict}
            )
            ensemble = EnsembleRetriever(
                retrievers=[filtered_retriever, self.bm25_retriever],
                weights=[0.6, 0.4],
            )
            results = await ensemble.ainvoke(query)
        else:
            results = await self.ensemble_retriever.ainvoke(query)

        return results[: self.top_k]
