import unittest
from document_processor import DocumentProcessor


class TestDocumentProcessor(unittest.TestCase):
    def setUp(self):
        self.processor = DocumentProcessor(
            model_encoding="cl100k_base", chunk_size=30, chunk_overlap=4
        )

    def test_constructor_parameter_validation(self):
        """Verifica que el constructor lance ValueError ante configuraciones inconsistentes."""
        # 1. Overlap mayor o igual al chunk_size
        with self.assertRaises(ValueError):
            DocumentProcessor(chunk_size=50, chunk_overlap=50)

        with self.assertRaises(ValueError):
            DocumentProcessor(chunk_size=50, chunk_overlap=60)

        # 2. Valores negativos o cero
        with self.assertRaises(ValueError):
            DocumentProcessor(chunk_size=0, chunk_overlap=0)

        with self.assertRaises(ValueError):
            DocumentProcessor(chunk_size=50, chunk_overlap=-5)

    def test_clean_text_normalization_and_unicode(self):
        """Verifica que regex elimine espacios repetidos, saltos excesivos y normalice ligaduras Unicode."""
        dirty = "La ﬁdelidad    del RAG.\n\n\n\nEste   es   un   texto   con   ruido.   "
        cleaned = self.processor.clean_text(dirty)
        self.assertEqual(
            cleaned, "La fidelidad del RAG.\n\nEste es un texto con ruido."
        )

    def test_calculate_tokens_accuracy(self):
        """Verifica el cálculo exacto de tokens con tiktoken."""
        text = "Generative AI Engineering"
        tokens = self.processor.calculate_tokens(text)
        self.assertGreater(tokens, 0)
        self.assertEqual(tokens, 4)

    def test_chunk_size_respects_token_limit(self):
        """Verifica que ningún chunk supere el límite de tokens configurado."""
        long_text = (
            "La arquitectura RAG permite conectar modelos de lenguaje con bases de datos vectoriales "
            "externas para responder preguntas complejas sin alucinar. Al fragmentar documentos grandes, "
            "debemos asegurar que los fragmentos no excedan la capacidad máxima de tokens del modelo."
        )
        chunks = self.processor.process_document(long_text)
        self.assertGreater(len(chunks), 1)

        for chunk in chunks:
            token_count = self.processor.calculate_tokens(chunk)
            self.assertLessEqual(token_count, self.processor.chunk_size)

    def test_metadata_enrichment(self):
        """Verifica el enriquecimiento con metadatos estructurados."""
        text = "Primer párrafo de prueba.\n\nSegundo párrafo de prueba."
        enriched = self.processor.process_document_with_metadata(
            text, source_metadata={"source": "test_doc.pdf"}
        )
        self.assertGreater(len(enriched), 0)
        first = enriched[0]
        self.assertIn("chunk_id", first)
        self.assertIn("token_count", first)
        self.assertIn("metadata", first)
        self.assertEqual(first["metadata"]["source"], "test_doc.pdf")

    def test_empty_document_handling(self):
        """Verifica que textos vacíos o de puros espacios retornen lista vacía."""
        self.assertEqual(self.processor.process_document(""), [])
        self.assertEqual(self.processor.process_document("   \n\n   "), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
