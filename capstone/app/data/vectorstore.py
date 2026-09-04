"""Gestor persistente de base de datos vectorial ChromaDB para RAG."""

import os
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.config import Settings as ChromaSettings
from chromadb.utils import embedding_functions
from app.config import settings


class VectorStoreManager:
    """Encapsula operaciones CRUD y búsqueda por similitud en ChromaDB."""

    def __init__(self):
        os.makedirs(settings.chroma_persist_directory, exist_ok=True)
        self.client = chromadb.PersistentClient(
            path=settings.chroma_persist_directory,
            settings=ChromaSettings(anonymized_telemetry=False),
        )

        if settings.openai_api_key and not settings.openai_api_key.startswith("tu_"):
            self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                api_key=settings.openai_api_key,
                model_name=settings.openai_embedding_model,
            )
        else:
            self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

        self.collection = self.client.get_or_create_collection(
            name=settings.chroma_collection_name,
            embedding_function=self.embedding_fn,
            metadata={"hnsw:space": "cosine"},
        )

    def upsert_chunks(
        self,
        ids: List[str],
        documents: List[str],
        metadatas: List[Dict[str, Any]],
    ) -> int:
        """Inserta o actualiza fragmentos documentales con sus metadatos."""
        if not ids:
            return 0
        self.collection.upsert(ids=ids, documents=documents, metadatas=metadatas)
        return len(ids)

    def similarity_search(
        self, query: str, top_k: int = 3, filter_criteria: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Realiza búsqueda semántica en la colección vectorial."""
        if self.collection.count() == 0:
            return []

        results = self.collection.query(
            query_texts=[query],
            n_results=min(top_k, self.collection.count()),
            where=filter_criteria,
            include=["documents", "metadatas", "distances"],
        )

        output: List[Dict[str, Any]] = []
        if not results or not results["ids"] or not results["ids"][0]:
            return output

        for i in range(len(results["ids"][0])):
            output.append({
                "id": results["ids"][0][i],
                "document": results["documents"][0][i],
                "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                "distance": results["distances"][0][i] if results["distances"] else 0.0,
            })
        return output


vector_store = VectorStoreManager()
