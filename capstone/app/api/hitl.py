"""Controlador de supervisión humana Human-in-the-Loop (HITL)."""

from typing import Any, Dict, Optional
from app.api.store import task_store


async def process_hitl_decision(
    job_id: str, approved: bool, feedback: Optional[str] = ""
) -> Dict[str, Any]:
    """Registra la resolución humana para un trabajo suspendido y reactiva el flujo."""
    task = await task_store.get_task(job_id)
    if not task:
        return {"ok": False, "error": "Trabajo no encontrado"}

    if task.get("status") != "waiting_human_approval":
        return {
            "ok": False,
            "error": f"El trabajo no está esperando aprobación (estado: {task.get('status')})",
        }

    # Actualizar estado de la tarea con la decisión humana
    task["hitl_approved"] = approved
    task["hitl_feedback"] = feedback or ("Aprobado por operador" if approved else "Rechazado")
    task["status"] = "pending"  # Re-encolar para que el worker finalice la síntesis
    task["progress_pct"] = 80

    await task_store.set_task(job_id, task)
    await task_store.enqueue_task(job_id)

    return {
        "ok": True,
        "job_id": job_id,
        "status": "pending",
        "hitl_approved": approved,
        "feedback": task["hitl_feedback"],
    }
