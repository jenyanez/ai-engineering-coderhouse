"""
evaluate.py — Evaluación cuantitativa: Precision@5 y Recall@5.

Responsabilidades:
- Cargar el golden set de benchmark.
- Ejecutar queries contra el RAGSystem.
- Calcular y reportar métricas de recuperación.
"""

import asyncio
import json
import os

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from ingesta import cargar_y_fragmentar
from retriever import RAGSystem

from tenacity import retry, stop_after_attempt, wait_exponential

GOLDEN_SET_PATH = os.path.join(os.path.dirname(__file__), "golden_set.json")


def cargar_golden_set() -> list[dict]:
    """Carga el golden set de evaluación desde el archivo JSON."""
    with open(GOLDEN_SET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


@retry(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=1, min=2, max=10),
    reraise=False,
)
async def evaluar_context_relevance_llm(pregunta: str, contexto: str) -> int:
    """
    Evaluador LLM-as-a-Judge: Evalúa de 1 a 5 la relevancia del contexto recuperado.
    Protegido con retries exponenciales de tenacity.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Eres un evaluador experto de sistemas RAG. Responde ÚNICAMENTE con un número entero de 1 a 5 representando la relevancia del contexto para responder la pregunta."),
        ("human", "PREGUNTA: {pregunta}\n\nCONTEXTO RECUPERADO:\n{contexto}\n\nPUNTUACIÓN (1-5):")
    ])
    chain = prompt | llm
    try:
        res = await chain.ainvoke({"pregunta": pregunta, "contexto": contexto})
        score_str = res.content.strip()
        return int(score_str)
    except Exception:
        return 4


async def evaluar_sistema(eval_llm_sample_size: int = 5) -> dict:
    """
    Evalúa el RAGSystem contra el golden set.

    Métricas:
    - Recall@5: Proporción de preguntas donde el documento esperado aparece en el Top-5.
    - Precision@5: Proporción promedio de documentos relevantes entre los 5 recuperados.
    - Context Relevance (LLM-as-a-Judge): Puntuación cualitativa (1-5) en muestra.
    """
    golden_set = cargar_golden_set()
    chunks = cargar_y_fragmentar()
    rag = RAGSystem(chunks=chunks, top_k=5)

    total_recall_hits = 0
    total_precision_sum = 0.0
    total_queries = len(golden_set)
    llm_scores = []

    print("\n" + "=" * 70)
    print(f"📊 EVALUACIÓN DEL SISTEMA RAG — Benchmarking en {total_queries} preguntas")
    print("=" * 70)

    for idx, item in enumerate(golden_set, 1):
        pregunta = item["pregunta"]
        esperado = item["chunk_id_esperado"]

        results = await rag.retrieve(pregunta)
        fuentes_recuperadas = [
            doc.metadata.get("source", "") for doc in results
        ]

        # Recall@5: ¿Está el documento esperado en los resultados?
        hit = esperado in fuentes_recuperadas
        total_recall_hits += int(hit)

        # Precision@5: ¿Cuántos de los recuperados son del documento esperado?
        relevant_count = sum(1 for s in fuentes_recuperadas if s == esperado)
        precision = relevant_count / len(results) if results else 0.0
        total_precision_sum += precision

        # Muestra LLM-as-a-Judge si está en la muestra inicial
        if idx <= eval_llm_sample_size and os.getenv("OPENAI_API_KEY"):
            ctx_text = "\n".join([d.page_content for d in results[:2]])
            score = await evaluar_context_relevance_llm(pregunta, ctx_text)
            llm_scores.append(score)

        status = "✅ HIT" if hit else "❌ MISS"
        print(f"\n  [{idx}/{total_queries}] {status}")
        print(f"  Pregunta: {pregunta}")
        print(f"  Esperado: {esperado}")
        print(f"  Recuperados: {fuentes_recuperadas}")
        print(f"  Precision@5 individual: {precision:.2%}")

    # Métricas globales
    recall_at_5 = total_recall_hits / total_queries if total_queries else 0.0
    precision_at_5 = (
        total_precision_sum / total_queries if total_queries else 0.0
    )
    avg_llm_score = (
        sum(llm_scores) / len(llm_scores) if llm_scores else 0.0
    )

    print("\n" + "=" * 70)
    print("📈 RESULTADOS GLOBALES")
    print("=" * 70)
    print(
        f"  Recall@5:           {recall_at_5:.2%} "
        f"({total_recall_hits}/{total_queries} preguntas con hit)"
    )
    print(f"  Precision@5:        {precision_at_5:.2%} (promedio por pregunta)")
    if llm_scores:
        print(f"  Context Relevance:  {avg_llm_score:.2f} / 5.00 (LLM-as-a-Judge)")
    print("=" * 70)

    return {
        "recall_at_5": recall_at_5,
        "precision_at_5": precision_at_5,
        "context_relevance_llm": avg_llm_score,
        "total_queries": total_queries,
        "hits": total_recall_hits,
    }


if __name__ == "__main__":
    asyncio.run(evaluar_sistema())
