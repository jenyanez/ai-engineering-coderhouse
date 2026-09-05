"""Worker asíncrono en segundo plano para ejecución desacoplada del grafo."""

import asyncio
import logging
import time
from app.agents.graph import intelligence_graph
from app.api.store import task_store

logger = logging.getLogger("AsyncWorker")


async def run_task_job(job_id: str) -> None:
    """Ejecuta una tarea individual mediante el grafo multi-agente."""
    task = await task_store.get_task(job_id)
    if not task:
        return

    start_time = time.perf_counter()
    task["status"] = "processing"
    task["progress_pct"] = max(task.get("progress_pct", 10), 30)
    await task_store.set_task(job_id, task)

    config = {"configurable": {"thread_id": job_id}}
    initial_input = {
        "query": task["query"],
        "messages": [],
        "research_data": task.get("research_data"),
        "analysis_data": task.get("analysis_data"),
        "review_data": task.get("review_data"),
        "final_summary": task.get("final_summary"),
        "hitl_pending": False,
        "hitl_approved": task.get("hitl_approved"),
        "hitl_feedback": task.get("hitl_feedback"),
        "iteration_count": task.get("iteration_count", 0),
        "next_agent": "Investigador",
        "session_id": task.get("session_id", job_id),
    }

    try:
        # Invocación asíncrona no bloqueante
        result = await intelligence_graph.ainvoke(initial_input, config=config)
        elapsed = round(time.perf_counter() - start_time, 3)

        if result.get("final_summary"):
            task["final_summary"] = result["final_summary"]

        task["research_data"] = result.get("research_data") or task.get("research_data")
        task["analysis_data"] = result.get("analysis_data") or task.get("analysis_data")
        task["review_data"] = result.get("review_data") or task.get("review_data")
        task["duration_seconds"] = elapsed

        from app.config import settings
        from app.observability.finops import estimate_token_cost

        p_tokens = max(50, (len(task["query"]) + len(str(task.get("research_data") or ""))) // 4)
        c_tokens = max(50, len(str(result.get("final_summary") or "")) // 4)
        task["finops"] = estimate_token_cost(settings.openai_model, p_tokens, c_tokens)

        if result.get("hitl_pending") and task.get("hitl_approved") is None:
            task["status"] = "waiting_human_approval"
            task["progress_pct"] = 70
            task["message"] = "Ejecución pausada: Tarea crítica en espera de aprobación humana."
        else:
            task["status"] = "completed"
            task["progress_pct"] = 100
            task["result"] = result.get("final_summary") or task.get("final_summary")
            task["completed_at"] = time.strftime("%Y-%m-%d %H:%M:%S")

        await task_store.set_task(job_id, task)

    except Exception as err:
        logger.error(f"Error procesando tarea {job_id}: {err}", exc_info=True)
        task["status"] = "failed"
        task["error"] = str(err)
        task["duration_seconds"] = round(time.perf_counter() - start_time, 3)
        await task_store.set_task(job_id, task)


async def background_worker_loop() -> None:
    """Bucle infinito de consumo de cola Redis FIFO."""
    logger.info("Worker asíncrono de producción iniciado...")
    while True:
        try:
            job_id = await task_store.dequeue_task(timeout=1)
            if job_id:
                await run_task_job(job_id)
            else:
                await asyncio.sleep(0.1)
        except asyncio.CancelledError:
            break
        except Exception as err:
            logger.error(f"Error en worker loop: {err}")
            await asyncio.sleep(1)
