"""Procesador en segundo plano (Worker) con orquestación LangGraph, HITL y FinOps."""

from datetime import datetime, timezone
import logging, time
from typing import Any, Dict, Optional
from langchain_core.messages import HumanMessage

from app.finops import FinOpsAuditor
from app.graph import orchestrator_graph
from app.hitl import HITLManager
from app.state import AgentState, TaskStatus
from app.store import store

logger = logging.getLogger("Worker")


async def execute_task_background(job_id: str, query: str, require_approval: bool) -> None:
    """Ejecuta el grafo multi-agente en background con persistencia y manejo de excepciones."""
    now_iso, start_time = datetime.now(timezone.utc).isoformat(), time.time()
    task_data = await store.get_task(job_id) or {}
    task_data.update({"status": TaskStatus.RUNNING, "started_at": now_iso})
    await store.set_task(job_id, task_data)

    try:
        thread_config = {"configurable": {"thread_id": job_id}}
        init_state: AgentState = {
            "messages": [HumanMessage(content=query)], "next_agent": "Investigador", "query": query,
            "research_data": None, "analysis_data": None, "hitl_approved": None if require_approval else True,
            "hitl_feedback": None, "final_summary": None, "iteration_count": 0, "error": None,
        }
        current_state = orchestrator_graph.invoke(init_state, config=thread_config)
        finops = FinOpsAuditor.estimate_task_cost(query, was_rejected=False)

        if HITLManager.is_critical_operation(query, require_approval):
            inter_summary = HITLManager.format_intermediate_summary(
                current_state.get("research_data"), current_state.get("analysis_data")
            )
            task_data.update({
                "status": TaskStatus.WAITING_APPROVAL, "requires_approval": True,
                "intermediate_summary": inter_summary, "intermediate_state": current_state,
                "total_tokens": finops["total_tokens"], "estimated_cost_usd": finops["estimated_cost_usd"],
            })
            await store.set_task(job_id, task_data)
            return

        task_data.update({
            "status": TaskStatus.COMPLETED,
            "result": {"summary": current_state.get("final_summary"), "state": current_state},
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "execution_time_seconds": round(time.time() - start_time, 4),
            "total_tokens": finops["total_tokens"], "estimated_cost_usd": finops["estimated_cost_usd"],
        })
        await store.set_task(job_id, task_data)
    except Exception as exc:
        logger.error(f"Error procesando job {job_id}: {exc}")
        task_data.update({
            "status": TaskStatus.FAILED, "error": str(exc),
            "completed_at": datetime.now(timezone.utc).isoformat(),
            "execution_time_seconds": round(time.time() - start_time, 4),
        })
        await store.set_task(job_id, task_data)


async def resume_hitl_task(job_id: str, approved: bool, feedback: Optional[str]) -> Dict[str, Any]:
    """Reanuda la ejecución del grafo tras la decisión humana."""
    task_data = await store.get_task(job_id)
    if not task_data:
        raise ValueError(f"No existe la tarea {job_id}")

    saved_state = task_data.get("intermediate_state", {})
    saved_state.update({"hitl_approved": approved, "hitl_feedback": feedback or ""})
    resumed_state = orchestrator_graph.invoke(saved_state, config={"configurable": {"thread_id": job_id}})

    finops = FinOpsAuditor.estimate_task_cost(task_data.get("query", ""), was_rejected=not approved)
    task_data.update({
        "status": TaskStatus.COMPLETED if approved else TaskStatus.REJECTED,
        "requires_approval": False,
        "result": {"summary": resumed_state.get("final_summary"), "state": resumed_state},
        "completed_at": datetime.now(timezone.utc).isoformat(),
        "total_tokens": finops["total_tokens"], "estimated_cost_usd": finops["estimated_cost_usd"],
    })
    await store.set_task(job_id, task_data)
    return task_data
