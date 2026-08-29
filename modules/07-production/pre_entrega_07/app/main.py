"""API REST Asíncrona de Producción con FastAPI, Redis, Phoenix y HITL."""

from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import List, Optional
import uuid
from fastapi import BackgroundTasks, FastAPI, HTTPException, Query, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse

from app.config import settings
from app.dashboard_view import get_dashboard_html
from app.guardrails import SecurityGuardrails
from app.observability import setup_observability
from app.state import (
    ApprovalRequest,
    ApprovalResponse,
    TaskCreateRequest,
    TaskCreateResponse,
    TaskStatus,
    TaskStatusResponse,
)
from app.store import store
from app.worker import execute_task_background, resume_hitl_task


@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_observability()
    await store.get_client()
    yield


app = FastAPI(
    title=settings.API_TITLE,
    version=settings.API_VERSION,
    description=settings.API_DESCRIPTION,
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_credentials=True, allow_methods=["*"], allow_headers=["*"]
)


@app.get("/dashboard", response_class=HTMLResponse, tags=["Dashboard"], summary="Mission Control UI")
async def dashboard():
    """Interfaz web interactiva para monitoreo y aprobación HITL en vivo."""
    return HTMLResponse(content=get_dashboard_html())


@app.post(
    "/tasks",
    response_model=TaskCreateResponse,
    status_code=status.HTTP_202_ACCEPTED,
    tags=["Tareas Asíncronas"],
    summary="Encolar nueva tarea asíncrona (Non-blocking)",
)
async def create_task(request: TaskCreateRequest, background_tasks: BackgroundTasks):
    """Valida guardrails, genera el job_id y encola la ejecución sin bloquear la conexión."""
    is_safe, reason = SecurityGuardrails.validate_query(request.query)
    if not is_safe:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=reason)

    job_id = f"job_{uuid.uuid4().hex[:12]}"
    now_iso = datetime.now(timezone.utc).isoformat()
    task_data = {
        "job_id": job_id, "query": request.query, "priority": request.priority,
        "require_approval": request.require_human_approval, "status": TaskStatus.PENDING,
        "created_at": now_iso, "guardrail_status": "PASSED",
    }
    await store.set_task(job_id, task_data)

    background_tasks.add_task(
        execute_task_background,
        job_id=job_id, query=request.query, require_approval=request.require_human_approval,
    )
    return TaskCreateResponse(job_id=job_id, status=TaskStatus.PENDING, created_at=now_iso)


@app.get("/tasks", response_model=List[TaskStatusResponse], tags=["Tareas Asíncronas"], summary="Listar tareas")
async def list_tasks(limit: int = Query(default=50, le=100)):
    raw_tasks = await store.list_tasks(limit=limit)
    return [TaskStatusResponse(**t) for t in raw_tasks]


@app.get("/tasks/{job_id}", response_model=TaskStatusResponse, tags=["Tareas Asíncronas"], summary="Consultar estado")
async def get_task_status(job_id: str):
    task = await store.get_task(job_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trabajo '{job_id}' no encontrado")
    return TaskStatusResponse(**task)


@app.post("/tasks/{job_id}/approve", response_model=ApprovalResponse, tags=["Human-in-the-Loop"], summary="Aprobar HITL")
async def approve_task(job_id: str, request: ApprovalRequest):
    task = await store.get_task(job_id)
    if not task:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Trabajo '{job_id}' no encontrado")
    if task.get("status") != TaskStatus.WAITING_APPROVAL:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Estado no es WAITING_APPROVAL ({task.get('status')})")

    resumed = await resume_hitl_task(job_id=job_id, approved=request.approved, feedback=request.feedback)
    msg = "Tarea aprobada y síntesis completada." if request.approved else "Tarea rechazada por supervisor."
    return ApprovalResponse(job_id=job_id, status=resumed["status"], message=msg)


@app.get("/health", tags=["Monitoreo y Salud"], summary="Health check")
async def health_check():
    redis_active = await store.get_client() is not None
    return {
        "status": "healthy", "timestamp": datetime.now(timezone.utc).isoformat(),
        "services": {"api": "online", "redis": "connected" if redis_active else "persistent_disk_fallback", "phoenix": settings.PHOENIX_COLLECTOR_ENDPOINT},
    }


@app.get("/", include_in_schema=False)
async def root():
    return RedirectResponse(url="/dashboard")
