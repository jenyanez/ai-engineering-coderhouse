"""
task_group_runner.py — Orquestador utilizando asyncio.TaskGroup (Python 3.11+).

Proporciona una forma moderna y estructurada de concurrencia. A diferencia de 
asyncio.gather, si una de las tareas del grupo lanza una excepción, las demás 
se cancelan de forma segura e inmediata.
"""

import asyncio

from models.llm_simulators import claude_3_call, gpt_4_call, local_llama_call
from utils.logger import setup_logger

logger = setup_logger("orquestador")


async def run_task_group_gather() -> list[dict]:
    """
    Ejecuta 3 llamadas a modelos concurrentemente usando asyncio.TaskGroup.
    Recupera los resultados de manera segura una vez finalizado el grupo.

    Returns:
        Lista de resultados de los modelos.
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("DEMO 4: asyncio.TaskGroup — Concurrencia estructurada moderna")
    logger.info("=" * 60)

    semaphore = asyncio.Semaphore(3)
    results = []

    try:
        async with asyncio.TaskGroup() as tg:
            # Crear y registrar las tareas dentro del grupo
            task_gpt = tg.create_task(gpt_4_call(semaphore, call_id=3, latency=1.2))
            task_claude = tg.create_task(claude_3_call(semaphore, call_id=3, latency=0.8))
            task_llama = tg.create_task(local_llama_call(semaphore, call_id=3, latency=0.4))

        # Al salir del bloque, garantizamos que todas finalizaron con éxito
        results = [task_gpt.result(), task_claude.result(), task_llama.result()]

        logger.info("📊 Resultados Demo 4 (TaskGroup): %d respuestas recibidas", len(results))
        for r in results:
            logger.info("   → %s: %s", r["model"], r["response"])

    except Exception as e:
        logger.error("❌ Error en el TaskGroup: %s", str(e))

    return results