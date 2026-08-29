import shutil
import tempfile
import unittest
from typing import Dict, Any
from chromadb.api.types import Documents, EmbeddingFunction, Embeddings
from vector_memory_manager import VectorMemoryManager


class DummyEmbeddingFunction(EmbeddingFunction):
    """Función de embedding simulada para pruebas ultrarrápidas y deterministas."""

    def __init__(self):
        super().__init__()

    def name(self) -> str:
        return "dummy_embedding_fn"

    def get_config(self) -> Dict[str, Any]:
        return {}

    def __call__(self, input: Documents) -> Embeddings:
        # Genera un vector 3D determinista para cada texto
        return [[float(len(t) % 10), 1.0, 0.5] for t in input]


class TestVectorMemoryManager(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.embedding_fn = DummyEmbeddingFunction()
        self.manager = VectorMemoryManager(
            persist_path=self.temp_dir,
            collection_name="test_crud_coll",
            embedding_function=self.embedding_fn,
        )

    def tearDown(self):
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_upsert_and_count(self):
        """Verifica la inserción correcta y conteo de documentos."""
        self.manager.upsert_documents(
            ids=["id1", "id2"],
            documents=["Documento uno", "Documento dos"],
            metadatas=[{"tag": "a"}, {"tag": "b"}],
        )
        self.assertEqual(self.manager.count_documents(), 2)

    def test_automatic_deterministic_ids(self):
        """Verifica la generación de IDs basados en SHA-256 cuando no se proporcionan IDs."""
        ids = self.manager.upsert_documents(
            ids=None,
            documents=["Texto con hash determinista"],
            metadatas=[{"source": "auto"}],
        )
        self.assertEqual(len(ids), 1)
        self.assertTrue(ids[0].startswith("doc_"))
        self.assertEqual(self.manager.count_documents(), 1)

    def test_semantic_search_and_search_records(self):
        """Verifica que la búsqueda semántica y el formateador search_records funcionen."""
        self.manager.upsert_documents(
            ids=["id1", "id2"],
            documents=["Arquitecturas de agentes IA", "Persistencia en bases vectoriales"],
            metadatas=[{"type": "agent"}, {"type": "vectordb"}],
        )
        # 1. Búsqueda nativa
        results = self.manager.semantic_search("agentes", n_results=1)
        self.assertIn("documents", results)
        self.assertEqual(len(results["documents"][0]), 1)

        # 2. Búsqueda aplanada para LLMs
        records = self.manager.search_records("agentes", n_results=2)
        self.assertEqual(len(records), 2)
        self.assertIn("id", records[0])
        self.assertIn("document", records[0])
        self.assertIn("distance", records[0])

    def test_get_documents_with_filter(self):
        """Verifica la lectura exacta por metadato."""
        self.manager.upsert_documents(
            ids=["id1", "id2"],
            documents=["Texto A", "Texto B"],
            metadatas=[{"cat": "tech"}, {"cat": "finance"}],
        )
        exact = self.manager.get_documents(where_filter={"cat": "tech"})
        self.assertEqual(len(exact["ids"]), 1)
        self.assertEqual(exact["ids"][0], "id1")

    def test_update_via_upsert(self):
        """Verifica que upsert sobre un ID existente actualice el contenido sin duplicar."""
        self.manager.upsert_documents(["doc1"], ["Texto inicial"], [{"v": 1}])
        self.assertEqual(self.manager.count_documents(), 1)

        # Actualizar
        self.manager.upsert_documents(["doc1"], ["Texto modificado"], [{"v": 2}])
        self.assertEqual(self.manager.count_documents(), 1)
        updated = self.manager.get_documents(ids=["doc1"])
        self.assertEqual(updated["documents"][0], "Texto modificado")
        self.assertEqual(updated["metadatas"][0]["v"], 2)

    def test_delete_documents(self):
        """Verifica la eliminación por ID."""
        self.manager.upsert_documents(["d1", "d2"], ["Doc 1", "Doc 2"])
        self.assertEqual(self.manager.count_documents(), 2)

        self.manager.delete_documents(ids=["d1"])
        self.assertEqual(self.manager.count_documents(), 1)
        remaining = self.manager.get_documents()
        self.assertNotIn("d1", remaining["ids"])

    def test_validation_errors(self):
        """Verifica que se levante ValueError ante listas vacías o inconsistentes."""
        with self.assertRaises(ValueError):
            self.manager.upsert_documents(ids=[], documents=[])

        with self.assertRaises(ValueError):
            self.manager.upsert_documents(
                ids=["id1"], documents=["doc1"], metadatas=[{"a": 1}, {"b": 2}]
            )


if __name__ == "__main__":
    unittest.main(verbosity=2)
