"""Pipeline de ingesta, fragmentación recursiva e indexación en ChromaDB."""

import hashlib
import os
from typing import Dict, List
from langchain_text_splitters import RecursiveCharacterTextSplitter
from app.data.vectorstore import vector_store


def compute_chunk_hash(text: str) -> str:
    """Genera ID determinista basado en el contenido del fragmento."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def run_ingestion_pipeline(docs_dir: str = "data/knowledge_documents") -> Dict[str, int]:
    """Carga documentos, aplica chunking estructurado e indexa en ChromaDB."""
    if not os.path.exists(docs_dir):
        return {"documents": 0, "chunks": 0}

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=600,
        chunk_overlap=60,
        separators=["\n## ", "\n### ", "\n\n", "\n", ". ", " "],
    )

    all_ids: List[str] = []
    all_chunks: List[str] = []
    all_metadatas: List[Dict[str, str]] = []
    doc_count = 0

    for fname in os.listdir(docs_dir):
        if not fname.endswith((".md", ".txt")):
            continue

        doc_count += 1
        fpath = os.path.join(docs_dir, fname)
        with open(fpath, "r", encoding="utf-8") as f:
            content = f.read()

        splits = splitter.split_text(content)
        for idx, chunk in enumerate(splits):
            cid = f"{fname}_{idx}_{compute_chunk_hash(chunk)}"
            all_ids.append(cid)
            all_chunks.append(chunk)
            all_metadatas.append({
                "source": fname,
                "chunk_index": str(idx),
                "total_chunks": str(len(splits)),
            })

    total_upserted = vector_store.upsert_chunks(
        ids=all_ids, documents=all_chunks, metadatas=all_metadatas
    )

    return {"documents": doc_count, "chunks": total_upserted}


if __name__ == "__main__":
    result = run_ingestion_pipeline()
    print(f"Ingesta finalizada: {result['documents']} docs -> {result['chunks']} chunks.")
