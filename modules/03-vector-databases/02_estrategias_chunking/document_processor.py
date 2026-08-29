import re
import unicodedata
from typing import Any, Dict, List
import tiktoken
from langchain_text_splitters import RecursiveCharacterTextSplitter


class DocumentProcessor:
    """
    Procesador de documentos para arquitecturas RAG:
    1. Normalización Unicode NFKC y limpieza optimizada con regex precompiladas.
    2. Cálculo exacto de longitud en TOKENS utilizando tiktoken.
    3. Fragmentación semántica con RecursiveCharacterTextSplitter por tokens.
    """

    def __init__(
        self,
        model_encoding: str = "cl100k_base",
        chunk_size: int = 120,
        chunk_overlap: int = 15,
    ):
        # 1. Validación de parámetros de segmentación
        if chunk_size <= 0:
            raise ValueError(f"chunk_size debe ser > 0, recibido: {chunk_size}")
        if chunk_overlap < 0:
            raise ValueError(f"chunk_overlap debe ser >= 0, recibido: {chunk_overlap}")
        if chunk_overlap >= chunk_size:
            raise ValueError(
                f"chunk_overlap ({chunk_overlap}) debe ser estrictamente menor que chunk_size ({chunk_size})"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

        # 2. Inicializar el encoding de tiktoken
        try:
            self.tokenizer = tiktoken.get_encoding(model_encoding)
        except ValueError:
            self.tokenizer = tiktoken.encoding_for_model(model_encoding)

        # 3. Precompilar expresiones regulares para máximo rendimiento en CPU
        self._re_control = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
        self._re_spaces = re.compile(r"[ \t]+")
        self._re_line_edges = re.compile(r"^[ \t]+|[ \t]+$", re.MULTILINE)
        self._re_newlines = re.compile(r"\n{3,}")

        # 4. Configurar RecursiveCharacterTextSplitter basado en TOKENS
        self.splitter = RecursiveCharacterTextSplitter(
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            length_function=self.calculate_tokens,
            separators=["\n\n", "\n", ". ", " ", ""],
        )

    def clean_text(self, text: str) -> str:
        """Limpia el texto eliminando espacios duplicados, saltos excesivos y caracteres extraños."""
        if not text:
            return ""

        # Normalización Unicode canónica (elimina ligaduras tipo 'ﬁ' y normaliza caracteres)
        normalized = unicodedata.normalize("NFKC", text)

        # Limpieza mediante regex precompiladas
        cleaned = self._re_control.sub("", normalized)
        cleaned = self._re_spaces.sub(" ", cleaned)
        cleaned = self._re_line_edges.sub("", cleaned)
        cleaned = self._re_newlines.sub("\n\n", cleaned)

        return cleaned.strip()

    def calculate_tokens(self, text: str) -> int:
        """Calcula la cantidad exacta de tokens usando el tokenizer de tiktoken."""
        if not text:
            return 0
        return len(self.tokenizer.encode(text))

    def process_document(self, raw_text: str) -> List[str]:
        """Pipeline básico: Limpieza -> Fragmentación -> Retorno de Lista de Chunks."""
        cleaned_text = self.clean_text(raw_text)
        if not cleaned_text:
            return []
        return self.splitter.split_text(cleaned_text)

    def process_document_with_metadata(
        self, raw_text: str, source_metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """Pipeline enriquecido: Retorna chunks con metadatos para VectorStores (Chroma/Pinecone)."""
        chunks = self.process_document(raw_text)
        meta = source_metadata or {}
        enriched = []
        for i, chunk in enumerate(chunks, 1):
            enriched.append(
                {
                    "chunk_id": i,
                    "content": chunk,
                    "token_count": self.calculate_tokens(chunk),
                    "char_count": len(chunk),
                    "metadata": {**meta, "chunk_index": i, "total_chunks": len(chunks)},
                }
            )
        return enriched


if __name__ == "__main__":
    sample_text = """
    ====================== DOCUMENTO DE PRUEBA RAG ======================
    
    En la arquitectura RAG (Generación Aumentada por Recuperación), la calidad de la respuesta
    del LLM no depende únicamente del modelo base, sino fundamentalmente de la calidad y relevancia
    de los datos recuperados desde la base de datos vectorial.
    
    ¿Por qué necesitamos fragmentar (Chunking)?
    Los modelos de embeddings tienen ventanas de contexto limitadas. Si intentamos convertir
    un documento de 50 páginas en un único vector, perderemos los matices y detalles semánticos.
    El resultado será un promedio semántico diluido incapaz de responder preguntas puntuales.
    
    Estrategias Principales:
    1. Fixed-size: División por caracteres o tokens fijos (puede cortar oraciones a la mitad).
    2. Recursive Character Splitting: Respeta la jerarquía natural (párrafos, oraciones, palabras).
    3. Overlap: Permite solapamiento entre chunks para preservar continuidad temática.
    =====================================================================
    """

    # Proporción recomendada en la industria: 10-15% de overlap (ej. chunk_size=50, overlap=7 -> 14%)
    processor = DocumentProcessor(chunk_size=50, chunk_overlap=7)
    chunks_with_meta = processor.process_document_with_metadata(
        sample_text, source_metadata={"doc_name": "guia_rag.md", "autor": "Jen Yanez"}
    )

    print(f"📊 Total de chunks generados: {len(chunks_with_meta)}\n")
    for item in chunks_with_meta:
        print(f"--- [Chunk {item['chunk_id']}] ({item['token_count']} tokens | {item['char_count']} caracteres) ---")
        print(f"Metadatos: {item['metadata']}")
        print(f"Contenido:\n{item['content']}\n")
