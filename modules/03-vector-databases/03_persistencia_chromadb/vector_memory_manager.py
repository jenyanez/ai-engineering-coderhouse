import hashlib, logging, os
from typing import Any, Dict, List, Optional
import chromadb
from chromadb.errors import ChromaError
from chromadb.utils import embedding_functions

logger = logging.getLogger("VectorMemoryManager")


class VectorMemoryManager:
    """Gestor de memoria vectorial persistente con ChromaDB y manejo de excepciones de I/O."""

    def __init__(
        self, persist_path: str = "./data/chroma_db", collection_name: str = "agent_memory",
        embedding_function: Optional[Any] = None,
    ):
        self.persist_path = persist_path
        self.collection_name = collection_name
        try:
            os.makedirs(self.persist_path, exist_ok=True)
            self.client = chromadb.PersistentClient(path=self.persist_path)
            if embedding_function is not None:
                self.embedding_fn = embedding_function
            elif os.getenv("OPENAI_API_KEY"):
                try:
                    self.embedding_fn = embedding_functions.OpenAIEmbeddingFunction(
                        api_key=os.getenv("OPENAI_API_KEY"), model_name="text-embedding-3-small"
                    )
                except Exception:
                    self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()
            else:
                self.embedding_fn = embedding_functions.DefaultEmbeddingFunction()

            self.collection = self.client.get_or_create_collection(
                name=self.collection_name, embedding_function=self.embedding_fn,
                metadata={"hnsw:space": "cosine", "description": "Memoria persistente RAG"},
            )
        except Exception as e:
            logger.error(f"Error inicializando ChromaDB en {persist_path}: {e}")
            raise RuntimeError(f"Fallo al conectar con almacenamiento ChromaDB: {e}")

    def _generate_deterministic_ids(self, documents: List[str]) -> List[str]:
        return [f"doc_{hashlib.sha256(d.encode('utf-8')).hexdigest()[:16]}" for d in documents]

    def upsert_documents(
        self, ids: Optional[List[str]], documents: List[str],
        metadatas: Optional[List[Dict[str, Any]]] = None, batch_size: int = 100,
    ) -> List[str]:
        """Inserta o actualiza documentos con captura de excepciones de I/O."""
        if not documents:
            raise ValueError("La lista de documentos no puede estar vacía.")
        final_ids = ids if ids and len(ids) == len(documents) else self._generate_deterministic_ids(documents)
        if metadatas is not None and len(metadatas) != len(documents):
            raise ValueError("metadatas debe tener la misma longitud que documents.")
        try:
            for i in range(0, len(documents), batch_size):
                self.collection.upsert(
                    ids=final_ids[i : i + batch_size], documents=documents[i : i + batch_size],
                    metadatas=metadatas[i : i + batch_size] if metadatas is not None else None,
                )
            return final_ids
        except (ChromaError, Exception) as e:
            logger.error(f"Error de I/O en upsert_documents: {e}")
            raise RuntimeError(f"Error al persistir documentos en ChromaDB: {e}")

    def semantic_search(
        self, query_text: str, n_results: int = 3, where_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Realiza búsqueda semántica capturando excepciones de bajo nivel."""
        if not query_text:
            return {"ids": [[]], "documents": [[]], "distances": [[]], "metadatas": [[]]}
        try:
            total = self.collection.count()
            if total == 0:
                return {"ids": [[]], "documents": [[]], "distances": [[]], "metadatas": [[]]}
            return self.collection.query(query_texts=[query_text], n_results=min(n_results, total), where=where_filter)
        except (ChromaError, Exception) as e:
            logger.error(f"Error de I/O en semantic_search: {e}")
            return {"ids": [[]], "documents": [[]], "distances": [[]], "metadatas": [[]], "error": str(e)}

    def search_records(
        self, query_text: str, n_results: int = 3, where_filter: Optional[Dict[str, Any]] = None
    ) -> List[Dict[str, Any]]:
        """Retorna registros aplanados listos para prompts de LLMs."""
        try:
            raw = self.semantic_search(query_text, n_results=n_results, where_filter=where_filter)
            records = []
            if raw.get("ids") and raw["ids"][0]:
                for i, id_ in enumerate(raw["ids"][0]):
                    records.append({
                        "id": id_, "document": raw["documents"][0][i], "distance": raw["distances"][0][i],
                        "metadata": raw["metadatas"][0][i] if raw.get("metadatas") else {},
                    })
            return records
        except Exception as e:
            logger.error(f"Error en search_records: {e}")
            return []

    def get_documents(
        self, ids: Optional[List[str]] = None, where_filter: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Recupera documentos exactos con captura de excepciones."""
        try:
            return self.collection.get(ids=ids, where=where_filter)
        except (ChromaError, Exception) as e:
            logger.error(f"Error de I/O en get_documents: {e}")
            return {"ids": [], "documents": [], "metadatas": [], "error": str(e)}

    def delete_documents(
        self, ids: Optional[List[str]] = None, where_filter: Optional[Dict[str, Any]] = None
    ) -> None:
        """Elimina vectores por IDs o metadatos con control de excepciones."""
        try:
            self.collection.delete(ids=ids, where=where_filter)
        except (ChromaError, Exception) as e:
            logger.error(f"Error de I/O en delete_documents: {e}")
            raise RuntimeError(f"Error al eliminar documentos en ChromaDB: {e}")

    def count_documents(self) -> int:
        """Retorna la cantidad total de documentos."""
        try:
            return self.collection.count()
        except Exception as e:
            logger.error(f"Error en count_documents: {e}")
            return 0


if __name__ == "__main__":
    manager = VectorMemoryManager(persist_path="./data/chroma_demo", collection_name="demo_crud_io")
    docs = ["LangGraph orquesta agentes.", "ChromaDB persiste vectores.", "FastAPI expone endpoints."]
    metas = [{"cat": "agentes"}, {"cat": "vectordb"}, {"cat": "api"}]

    print(f"📥 Insertando {len(docs)} documentos...")
    manager.upsert_documents(ids=None, documents=docs, metadatas=metas)
    print(f"📊 Total en colección: {manager.count_documents()} documentos.")

    print("\n🔍 Búsqueda semántica:")
    for r in manager.search_records("vectores y almacenamiento", n_results=2):
        print(f"  • [Dist: {r['distance']:.4f}] -> {r['document']}")

    print("\n🗑️ Eliminando documento por metadato ({'cat': 'api'})...")
    manager.delete_documents(where_filter={"cat": "api"})
    print(f"📊 Total restante: {manager.count_documents()} documentos.")
