"""
concurrent_runner.py — Orquestador concurrente de modelos LLM.

Implementa tres demos progresivas:
  1. Gather básico: 3 llamadas simultáneas.
  2. Timeout resiliente: asyncio.timeout (Python 3.11+) con manejo de error.
  3. Escalado con Semaphore: 10 llamadas, máximo 2 concurrentes.
"""

import asyncio
import random

from models.llm_simulators import claude_3_call, gpt_4_call, local_llama_call
from utils.logger import setup_logger

logger = setup_logger("orquestador")

# ── Catálogo de modelos disponibles ──────────────────────────────────────
MODEL_CATALOG = [gpt_4_call, claude_3_call, local_llama_call]


# ─────────────────────────────────────────────────────────────────────────
# DEMO 1: asyncio.gather — Disparo simultáneo de 3 llamadas
# ─────────────────────────────────────────────────────────────────────────
async def run_basic_gather() -> list[dict]:
    """
    Dispara 3 llamadas a modelos distintos de forma simultánea con
    asyncio.gather(). El Semaphore con valor alto (sin restricción real)
    permite ver que arrancan TODAS al mismo tiempo en los logs.

    Returns:
        Lista con las respuestas de cada modelo.
    """
    logger.info("=" * 60)
    logger.info("DEMO 1: asyncio.gather — 3 llamadas simultáneas")
    logger.info("=" * 60)

    # Semaphore permisivo (3) → todas arrancan al instante
    semaphore = asyncio.Semaphore(3)

    results = await asyncio.gather(
        gpt_4_call(semaphore, call_id=1),
        claude_3_call(semaphore, call_id=1),
        local_llama_call(semaphore, call_id=1),
    )

    logger.info("📊 Resultados Demo 1: %d respuestas recibidas", len(results))
    for result in results:
        logger.info("   → %s: %s", result["model"], result["response"])

    return results


# ─────────────────────────────────────────────────────────────────────────
# DEMO 2: asyncio.timeout — Resiliencia ante latencia excesiva
# ─────────────────────────────────────────────────────────────────────────
async def run_with_timeout(timeout_seconds: float = 2.0) -> list[dict]:
    """
    Ejecuta las 3 llamadas con un timeout global de N segundos.
    Si alguna tarda más, captura TimeoutError y reporta sin detenerse.

    Nota: Se fuerza una latencia de 3s en GPT-4 para demostrar el
    manejo de la excepción.

    Args:
        timeout_seconds: Límite de tiempo en segundos.

    Returns:
        Lista de respuestas (vacía si hubo timeout).
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info("DEMO 2: asyncio.timeout — Límite de %ss", timeout_seconds)
    logger.info("=" * 60)

    semaphore = asyncio.Semaphore(3)

    try:
        # asyncio.timeout es un context manager de Python 3.11+
        async with asyncio.timeout(timeout_seconds):
            results = await asyncio.gather(
                # Latencia forzada a 3s → excederá el timeout de 2s
                gpt_4_call(semaphore, call_id=2, latency=3.0),
                claude_3_call(semaphore, call_id=2, latency=1.0),
                local_llama_call(semaphore, call_id=2, latency=0.5),
            )
            return results

    except TimeoutError:
        logger.warning(
            "⏰ TIMEOUT: La ejecución excedió el límite de %.1fs. "
            "Llamada(s) cancelada(s) automáticamente.",
            timeout_seconds,
        )
        logger.info("💡 El programa continúa ejecutándose con normalidad.")
        return []


# ─────────────────────────────────────────────────────────────────────────
# DEMO 3: Semaphore — 10 llamadas, máximo 2 concurrentes
# ─────────────────────────────────────────────────────────────────────────
async def run_scaled_with_semaphore(
    total_calls: int = 10,
    max_concurrent: int = 2,
) -> list[dict]:
    """
    Dispara N simulaciones de llamadas a modelos, pero limita la
    concurrencia real a max_concurrent usando asyncio.Semaphore.

    En los logs se observará que solo max_concurrent tareas inician
    simultáneamente; las demás esperan su turno.

    Args:
        total_calls: Cantidad total de llamadas a simular.
        max_concurrent: Máximo de llamadas ejecutándose a la vez.

    Returns:
        Lista con todas las respuestas recopiladas.
    """
    logger.info("")
    logger.info("=" * 60)
    logger.info(
        "DEMO 3: Semaphore(%d) — %d llamadas, máx %d concurrentes",
        max_concurrent,
        total_calls,
        max_concurrent,
    )
    logger.info("=" * 60)

    # Semaphore restrictivo: solo 2 corrutinas activas a la vez
    semaphore = asyncio.Semaphore(max_concurrent)

    # Construir lista de tareas seleccionando modelos al azar
    tasks = []
    for i in range(total_calls):
        model_fn = random.choice(MODEL_CATALOG)
        # Latencia aleatoria entre 0.3s y 1.2s para variedad
        latency = round(random.uniform(0.3, 1.2), 1)
        tasks.append(model_fn(semaphore, call_id=i + 1, latency=latency))

    results = await asyncio.gather(*tasks)

    logger.info("📊 Resultados Demo 3: %d/%d respuestas recibidas", len(results), total_calls)
    return results