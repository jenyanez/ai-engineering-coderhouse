"""
main.py — Punto de entrada del Orquestador Concurrente de Modelos LLM.

Clase 1: Arquitectura Asíncrona con Python 3.12
Curso: AI Engineering (IA & Automatización) — Coderhouse

Ejecuta tres demostraciones progresivas:
  1. asyncio.gather  → 3 llamadas simultáneas.
  2. asyncio.timeout → Resiliencia ante latencia excesiva (2s).
  3. Semaphore(2)    → 10 llamadas con concurrencia controlada.

Requisitos:
  - Python 3.12+
  - No se usan dependencias externas (solo stdlib).

Ejecución:
  python main.py
"""

import asyncio
import time

from orchestrator.concurrent_runner import (
    run_basic_gather,
    run_scaled_with_semaphore,
    run_with_timeout,
)
from orchestrator.task_group_runner import run_task_group_gather
from utils.logger import setup_logger

logger = setup_logger("orquestador")


async def main() -> None:
    """Función principal que ejecuta las 4 demos secuencialmente."""

    logger.info("🏁 Orquestador Concurrente de Modelos LLM")
    logger.info("   Python %s | asyncio event loop activo", "3.12+")
    logger.info("")

    inicio_total = time.perf_counter()

    # ── Demo 1: Gather básico ────────────────────────────────────────
    inicio = time.perf_counter()
    await run_basic_gather()
    logger.info("⏱️  Demo 1 completada en %.2fs", time.perf_counter() - inicio)

    # ── Demo 2: Timeout resiliente ───────────────────────────────────
    inicio = time.perf_counter()
    await run_with_timeout(timeout_seconds=2.0)
    logger.info("⏱️  Demo 2 completada en %.2fs", time.perf_counter() - inicio)

    # ── Demo 3: Semaphore con 10 llamadas ────────────────────────────
    inicio = time.perf_counter()
    await run_scaled_with_semaphore(total_calls=10, max_concurrent=2)
    logger.info("⏱️  Demo 3 completada en %.2fs", time.perf_counter() - inicio)

    # ── Demo 4: TaskGroup moderno ────────────────────────────────────
    inicio = time.perf_counter()
    await run_task_group_gather()
    logger.info("⏱️  Demo 4 (TaskGroup) completada en %.2fs", time.perf_counter() - inicio)

    # ── Resumen final ────────────────────────────────────────────────
    logger.info("")
    logger.info("=" * 60)
    logger.info(
        "✅ Todas las demos finalizadas en %.2fs",
        time.perf_counter() - inicio_total,
    )
    logger.info("=" * 60)


if __name__ == "__main__":
    asyncio.run(main())