import argparse
import asyncio
import logging

from ingesta import indexar_documentos, cargar_y_fragmentar
from retriever import RAGSystem
from evaluate import evaluar_sistema

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


async def demo_query(rag: RAGSystem, query: str) -> None:
    """Ejecuta una consulta de demostración y muestra los resultados."""
    print(f"\n🔍 Consulta: '{query}'")
    results = await rag.retrieve(query)
    for i, doc in enumerate(results, 1):
        source = doc.metadata.get("source", "desconocida")
        category = doc.metadata.get("category", "N/A")
        preview = doc.page_content[:120].replace("\n", " ")
        print(f"  [{i}] {source} ({category}): {preview}...")


async def main():
    """Punto de entrada principal con soporte para banderas CLI."""
    parser = argparse.ArgumentParser(
        description="Sistema RAG Escalable en la Nube con Pinecone (Pre-Entrega 04)"
    )
    parser.add_argument(
        "--ingest", action="store_true", help="Ejecutar solo el pipeline de ingesta a Pinecone"
    )
    parser.add_argument(
        "--demo", action="store_true", help="Ejecutar solo la demostración de consultas e híbridas"
    )
    parser.add_argument(
        "--evaluate", action="store_true", help="Ejecutar solo la evaluación cuantitativa de 30 preguntas"
    )
    args = parser.parse_args()

    run_all = not (args.ingest or args.demo or args.evaluate)

    # 1. Ingesta Idempotente con Hashing SHA-256
    if args.ingest or run_all:
        logger.info("📥 Paso 1: Ingesta idempotente de documentos a Pinecone...")
        indexar_documentos()

    # 2. Demo de consulta híbrida con filtrado por metadatos
    if args.demo or run_all:
        logger.info("🔍 Paso 2: Consulta de ejemplo con recuperador híbrido y filtro por metadatos...")
        chunks = cargar_y_fragmentar()
        rag = RAGSystem(chunks=chunks, top_k=5)

        await demo_query(
            rag, "¿Cómo ayuda la IA a predecir el abandono de clientes?"
        )

        print("\n🎯 Demo de Filtrado por Metadatos (category = 'Estrategia Ia Ventas'):")
        results_filtrados = await rag.retrieve(
            "¿Cómo personalizar ofertas de venta?",
            filter_dict={"category": {"$eq": "Estrategia Ia Ventas"}},
        )
        for i, doc in enumerate(results_filtrados, 1):
            print(f"  [{i}] {doc.metadata.get('source')} ({doc.metadata.get('category')}): {doc.page_content[:100]}...")

    # 3. Evaluación cuantitativa (30 preguntas + LLM-as-a-Judge)
    if args.evaluate or run_all:
        logger.info("📊 Paso 3: Evaluación cuantitativa (Precision@5, Recall@5, LLM-as-a-Judge)...")
        await evaluar_sistema()


if __name__ == "__main__":
    asyncio.run(main())
