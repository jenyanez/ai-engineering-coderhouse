"""Modelos de datos Pydantic para la API y esquema de estado para LangGraph."""

from enum import Enum
from typing import Annotated, Any, Dict, List, Literal, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field


class TaskStatus(str, Enum):
    """Estados del ciclo de vida de un trabajo asíncrono."""
    PENDING = "PENDING"
    RUNNING = "RUNNING"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"
    REJECTED = "REJECTED"


class TaskCreateRequest(BaseModel):
    """Payload para crear y encolar una nueva tarea asíncrona."""
    query: str = Field(..., min_length=3, description="Pregunta o instrucción para el sistema multi-agente")
    priority: str = Field(default="normal", description="Prioridad de la tarea (low, normal, high)")
    require_human_approval: bool = Field(default=True, description="Si requiere aprobación humana (HITL) antes de sintetizar")


class TaskCreateResponse(BaseModel):
    """Respuesta inmediata al encolar una tarea (HTTP 202 Accepted)."""
    job_id: str = Field(..., description="Identificador único del trabajo")
    status: TaskStatus = Field(default=TaskStatus.PENDING, description="Estado inicial")
    message: str = Field(default="Tarea encolada exitosamente para procesamiento asíncrono.")
    created_at: str = Field(..., description="Marca de tiempo ISO-8601 de creación")


class TaskStatusResponse(BaseModel):
    """Respuesta detallada de consulta de estado (Polling)."""
    job_id: str
    status: TaskStatus
    query: str
    requires_approval: bool = False
    intermediate_summary: Optional[str] = None
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: str
    started_at: Optional[str] = None
    completed_at: Optional[str] = None
    execution_time_seconds: Optional[float] = None
    estimated_cost_usd: Optional[float] = None
    total_tokens: Optional[int] = None
    guardrail_status: Optional[str] = "PASSED"


class ApprovalRequest(BaseModel):
    """Payload para emitir una decisión humana en el nodo HITL."""
    approved: bool = Field(..., description="True para autorizar la síntesis, False para rechazar")
    feedback: Optional[str] = Field(default=None, description="Comentarios o directivas adicionales del supervisor")


class ApprovalResponse(BaseModel):
    """Respuesta tras procesar la aprobación humana."""
    job_id: str
    status: TaskStatus
    message: str


class AgentState(TypedDict):
    """Estado global compartido en el grafo multi-agente."""
    messages: Annotated[List[BaseMessage], add_messages]
    next_agent: Literal["Investigador", "Analista", "HITL", "Sintetizador", "FINALIZAR"]
    query: str
    research_data: Optional[Dict[str, Any]]
    analysis_data: Optional[Dict[str, Any]]
    hitl_approved: Optional[bool]
    hitl_feedback: Optional[str]
    final_summary: Optional[str]
    iteration_count: int
    error: Optional[str]
