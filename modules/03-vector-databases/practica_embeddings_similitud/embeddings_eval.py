"""
embeddings_eval.py — Evaluación empírica de Embeddings vs. TF-IDF usando scikit-learn.

Compara la Similitud Coseno de vectores densos (OpenAI Embeddings) frente a
representaciones léxicas (TF-IDF) para evaluar coincidencia semántica vs. palabras clave.
"""

import os
from typing import Dict, List, Tuple

from dotenv import load_dotenv
import numpy as np
from openai import OpenAI
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

load_dotenv()

# --- Conjunto de Datos de Evaluación ---
QUERY: str = "Despliegue e instalación de microservicios en un clúster de contenedores."

SEMANTIC_SENTENCES: List[Tuple[str, str]] = [
    ("S1", "Puesta en producción y aprovisionamiento de arquitectura basada en componentes independientes mediante pods de Kubernetes."),
    ("S2", "Lanzamiento y distribución de pequeños módulos de software empaquetados en un entorno virtualizado."),
    ("S3", "Publicación automatizada y ejecución de servicios desacoplados utilizando imágenes de Docker."),
    ("S4", "Inicialización de unidades funcionales aisladas dentro de una infraestructura distribuida de cómputo."),
    ("S5", "Puesta en marcha y coordinación de micro-aplicaciones conteinerizadas dentro de un nodo de procesamiento."),
]

TRAP_SENTENCES: List[Tuple[str, str]] = [
    ("T1 (Trampa Aseo)", "El servicio de micro-limpieza de alfombras y desinfección es excelente para oficinas pequeñas."),
    ("T2 (Trampa Logística)", "Se canceló el despliegue del contenedor marítimo de carga pesada debido a la huelga en el puerto de transporte."),
]


def compute_tfidf_similarities(query: str, corpus: List[str]) -> np.ndarray:
    """Calcula la similitud coseno basada en matriz TF-IDF (búsqueda léxica)."""
    vectorizer = TfidfVectorizer()
    all_texts = [query] + corpus
    tfidf_matrix = vectorizer.fit_transform(all_texts)
    # Similitud coseno entre la query (índice 0) y el resto del corpus
    similarities = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:]).flatten()
    return similarities


def compute_openai_embeddings_similarities(query: str, corpus: List[str]) -> np.ndarray:
    """Calcula la similitud coseno basada en OpenAI Embeddings (text-embedding-3-small)."""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY no encontrada en las variables de entorno.")

    client = OpenAI(api_key=api_key)
    all_texts = [query] + corpus

    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=all_texts
    )
    embeddings = np.array([item.embedding for item in response.data])

    # Similitud coseno con scikit-learn
    similarities = cosine_similarity(embeddings[0:1], embeddings[1:]).flatten()
    return similarities


def run_evaluation() -> Dict[str, Dict[str, float]]:
    """Ejecuta la evaluación comparativa y retorna métricas clave."""
    all_items = SEMANTIC_SENTENCES + TRAP_SENTENCES
    corpus = [text for _, text in all_items]
    labels = [label for label, _ in all_items]

    tfidf_scores = compute_tfidf_similarities(QUERY, corpus)
    embedding_scores = compute_openai_embeddings_similarities(QUERY, corpus)

    results = {}
    for idx, label in enumerate(labels):
        results[label] = {
            "tfidf_cosine": float(tfidf_scores[idx]),
            "embedding_cosine": float(embedding_scores[idx]),
        }
    return results


if __name__ == "__main__":
    print("=" * 70)
    print("Evaluación de Embeddings vs. TF-IDF — Similitud Coseno (scikit-learn)")
    print("=" * 70)
    print(f"Query: \"{QUERY}\"\n")

    eval_results = run_evaluation()

    print(f"{'Etiqueta':<25} | {'TF-IDF (Léxico)':<18} | {'Embedding (Semántico)':<22} | {'Estado':<10}")
    print("-" * 80)
    for label, metrics in eval_results.items():
        tfidf = metrics["tfidf_cosine"]
        emb = metrics["embedding_cosine"]
        status = "✅ OK" if ("S" in label and emb > tfidf) or ("T" in label and emb < tfidf) else "⚠️ Revisar"
        print(f"{label:<25} | {tfidf:<18.4f} | {emb:<22.4f} | {status:<10}")

    print("=" * 70)
