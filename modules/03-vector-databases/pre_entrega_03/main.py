"""
main.py — Orquestador del sistema RAG.

Responsabilidades:
- Ejecutar la ingesta de documentos (si es necesario).
- Exponer get_rag_response() como función asíncrona principal.
- Ejecutar pruebas automáticas: pregunta con respuesta + pregunta trampa.
"""

import asyncio
import logging
import os

from ingesta import indexar_documentos
from retriever import crear_retriever, formatear_documentos
from chain import chain, parser_llm
from schemas import RespuestaLLM, RAGResponse

# Configuración de logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    datefmt="%H:%M:%S",
)
logger = logging.getLogger(__name__)


async def get_rag_response(query: str) -> RAGResponse:
    """
    Función asíncrona principal del sistema RAG.

    Flujo:
      a. Búsqueda de similitud en ChromaDB (async).
      b. Construcción del contexto con fragmentos recuperados.
      c. Llamada asíncrona al LLM vía cadena LCEL.
      d. Parseo a modelo Pydantic con fuentes verificables.

    Args:
        query: Pregunta del usuario.

    Returns:
        RAGResponse con respuesta, fuentes y cantidad de fragmentos.
    """
    # a. Recuperación de fragmentos relevantes
    retriever = crear_retriever()
    docs = await retriever.ainvoke(query)

    # b. Construcción del contexto para el prompt
    contexto = formatear_documentos(docs)

    # c. Llamada asíncrona al LLM
    salida_llm: RespuestaLLM = await chain.ainvoke({
        "contexto": contexto,
        "pregunta": query,
        "formato": parser_llm.get_format_instructions(),
    })

    # d. Ensamblado final con fuentes verificables y rutas relativas portátiles
    base_dir = os.path.dirname(__file__)
    fuentes = sorted(set(
        os.path.relpath(d.metadata.get("source"), base_dir)
        if d.metadata.get("source") else "desconocida"
        for d in docs
    ))

    return RAGResponse(
        respuesta=salida_llm.respuesta,
        fuentes=fuentes,
        fragmentos_recuperados=len(docs),
    )


async def ejecutar_pruebas():
    """Ejecuta las pruebas automáticas del sistema RAG."""

    print("\n" + "=" * 80)
    print("🧪 PRUEBA 1: Pregunta CON respuesta en los documentos")
    print("=" * 80)

    respuesta_ok = await get_rag_response(
        "¿Cómo ayuda la IA a predecir el abandono de clientes (churn) "
        "y qué modelos se utilizan?"
    )

    print(f"\n🤖 RESPUESTA: {respuesta_ok.respuesta}")
    print(f"📎 FUENTES: {', '.join(respuesta_ok.fuentes)}")
    print(f"🔢 Fragmentos usados: {respuesta_ok.fragmentos_recuperados}")

    print("\n" + "=" * 80)
    print("🧪 PRUEBA 2: Pregunta TRAMPA (sin respuesta en los documentos)")
    print("=" * 80)

    respuesta_trampa = await get_rag_response(
        "¿Cuál es el costo promedio de implementar un sistema de "
        "computación cuántica para optimización logística?"
    )

    print(f"\n🤖 RESPUESTA: {respuesta_trampa.respuesta}")
    print(f"📎 FUENTES: {', '.join(respuesta_trampa.fuentes)}")
    print(f"🔢 Fragmentos usados: {respuesta_trampa.fragmentos_recuperados}")

    print("\n" + "=" * 80)
    print("✅ Pruebas completadas")
    print("=" * 80)


async def main():
    """Punto de entrada principal: ingesta + pruebas."""

    # Paso 1: Ingesta de documentos (con chequeo anti-reindexado)
    logger.info("Iniciando ingesta de documentos...")
    indexar_documentos()

    # Paso 2: Pruebas automáticas
    logger.info("Ejecutando pruebas del sistema RAG...")
    await ejecutar_pruebas()


if __name__ == "__main__":
    asyncio.run(main())
