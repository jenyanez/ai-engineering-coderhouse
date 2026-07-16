"""
llm_simulators.py — Corrutinas que simulan llamadas a distintos modelos LLM.

Cada corrutina usa asyncio.sleep() (NO bloqueante) para simular la latencia
de red real de una API de IA. Reciben un Semaphore para controlar la
concurrencia máxima.

Nota: NO se usa time.sleep() en ningún lugar (anti-patrón bloqueante).
"""

import asyncio
from utils.logger import setup_logger

logger = setup_logger("orquestador")


async def gpt_4_call(
    semaphore: asyncio.Semaphore,
    call_id: int = 0,
    latency: float = 1.5,
) -> dict:
    """
    Simula una llamada a la API de GPT-4.

    Args:
        semaphore: Controla el máximo de llamadas concurrentes.
        call_id: Identificador de la llamada (útil al escalar a N llamadas).
        latency: Segundos de latencia simulada (default: 1.5s).

    Returns:
        Diccionario con el modelo, id y respuesta simulada.
    """
    async with semaphore:
        logger.info("🚀 [GPT-4 #%d] Inicio de llamada (latencia: %.1fs)", call_id, latency)
        await asyncio.sleep(latency)
        logger.info("✅ [GPT-4 #%d] Respuesta recibida", call_id)
        return {
            "model": "gpt-4",
            "call_id": call_id,
            "response": "Respuesta simulada de GPT-4",
        }


async def claude_3_call(
    semaphore: asyncio.Semaphore,
    call_id: int = 0,
    latency: float = 1.0,
) -> dict:
    """
    Simula una llamada a la API de Claude 3.

    Args:
        semaphore: Controla el máximo de llamadas concurrentes.
        call_id: Identificador de la llamada.
        latency: Segundos de latencia simulada (default: 1.0s).

    Returns:
        Diccionario con el modelo, id y respuesta simulada.
    """
    async with semaphore:
        logger.info("🚀 [Claude-3 #%d] Inicio de llamada (latencia: %.1fs)", call_id, latency)
        await asyncio.sleep(latency)
        logger.info("✅ [Claude-3 #%d] Respuesta recibida", call_id)
        return {
            "model": "claude-3",
            "call_id": call_id,
            "response": "Respuesta simulada de Claude 3",
        }


async def local_llama_call(
    semaphore: asyncio.Semaphore,
    call_id: int = 0,
    latency: float = 0.5,
) -> dict:
    """
    Simula una llamada a un modelo LLaMA local.

    Args:
        semaphore: Controla el máximo de llamadas concurrentes.
        call_id: Identificador de la llamada.
        latency: Segundos de latencia simulada (default: 0.5s).

    Returns:
        Diccionario con el modelo, id y respuesta simulada.
    """
    async with semaphore:
        logger.info("🚀 [LLaMA-local #%d] Inicio de llamada (latencia: %.1fs)", call_id, latency)
        await asyncio.sleep(latency)
        logger.info("✅ [LLaMA-local #%d] Respuesta recibida", call_id)
        return {
            "model": "llama-local",
            "call_id": call_id,
            "response": "Respuesta simulada de LLaMA local",
        }