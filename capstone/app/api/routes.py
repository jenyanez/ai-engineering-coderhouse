"""Endpoints de la API REST asíncrona de grado de producción."""

import time
import uuid
from typing import Any, Dict, List
from fastapi import APIRouter, HTTPException, status
from app.api.hitl import process_hitl_decision
from app.api.store import task_store
from app.core.state import HITLApprovalRequest, QueryRequest

router = APIRouter(prefix="/api/v1", tags=["Intelligence API"])


@router.post("/query", status_code=status.HTTP_202_ACCEPTED)
async def submit_query(payload: QueryRequest) -> Dict[str, Any]:
    """Recibe una consulta compleja, genera un ticket (job_id) y la encola."""
    job_id = str(uuid.uuid4())
    session_id = payload.session_id or f"session_{job_id[:8]}"

    task_data = {
        "job_id": job_id,
        "session_id": session_id,
        "query": payload.query,
        "status": "pending",
        "progress_pct": 5,
        "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "result": None,
        "error": None,
    }

    await task_store.set_task(job_id, task_data)
    await task_store.enqueue_task(job_id)

    return {
        "job_id": job_id,
        "session_id": session_id,
        "status": "pending",
        "poll_url": f"/api/v1/jobs/{job_id}",
    }


@router.get("/jobs/{job_id}")
async def get_job_status(job_id: str) -> Dict[str, Any]:
    """Endpoint de sondeo (polling) para consultar el estado y resultado del trabajo."""
    task = await task_store.get_task(job_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Trabajo con ID '{job_id}' no encontrado",
        )
    return task


@router.post("/jobs/{job_id}/approve")
async def approve_job(job_id: str, payload: HITLApprovalRequest) -> Dict[str, Any]:
    """Punto de intervención Human-in-the-Loop para reanudar tareas críticas."""
    result = await process_hitl_decision(
        job_id=job_id, approved=payload.approved, feedback=payload.feedback
    )
    if not result.get("ok"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=result.get("error")
        )
    return result


@router.get("/jobs", response_model=List[Dict[str, Any]])
async def list_recent_jobs() -> List[Dict[str, Any]]:
    """Lista los trabajos recientes registrados en el sistema."""
    return await task_store.list_tasks(limit=30)


@router.get("/health")
async def health_check() -> Dict[str, str]:
    """Liveness probe para balanceadores de carga y monitoreo."""
    return {"status": "healthy", "service": "Intelligence Production System"}
