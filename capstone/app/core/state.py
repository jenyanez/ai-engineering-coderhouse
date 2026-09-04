"""Esquemas de estado tipado para LangGraph y contratos de datos Pydantic."""

from typing import Annotated, Any, Dict, List, Literal, Optional
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field
from typing_extensions import TypedDict


# --- MODELOS PYDANTIC PARA VALIDACIÓN DE ENTRADA Y HERRAMIENTAS ---


class QueryRequest(BaseModel):
    """Contrato de entrada para la API."""

    query: str = Field(..., min_length=3, description="Consulta del usuario")
    session_id: Optional[str] = Field(
        default=None, description="ID de sesión para persistencia de contexto"
    )


class HITLApprovalRequest(BaseModel):
    """Contrato para resolución de Human-in-the-Loop."""

    approved: bool = Field(..., description="Veredicto humano (True/False)")
    feedback: Optional[str] = Field(
        default="", description="Observaciones o directivas adicionales"
    )


class ResearchPayload(BaseModel):
    """Contrato de salida validado para el Agente Investigador."""

    found_in_kb: bool = Field(default=True)
    topic: str = Field(default="")
    market_size_2024_usd_b: Optional[float] = Field(default=None)
    market_size_2030_usd_b: Optional[float] = Field(default=None)
    fortune_500_adoption_rate: Optional[str] = Field(default=None)
    key_drivers: List[str] = Field(default_factory=list)
    source: str = Field(default="")
    evidence_snippet: str = Field(default="")


class AnalysisPayload(BaseModel):
    """Contrato de salida validado para el Agente Analista."""

    valid_analysis: bool = Field(default=True)
    cagr_percentage: Optional[float] = Field(default=None)
    expansion_factor: Optional[float] = Field(default=None)
    interpretation: str = Field(default="")


class ReviewPayload(BaseModel):
    """Contrato de salida validado para el Agente Revisor."""

    is_grounded: bool = Field(default=True)
    quality_score: float = Field(default=1.0, ge=0.0, le=1.0)
    requires_hitl: bool = Field(default=False)
    audit_notes: str = Field(default="")


# --- ESTADO TIPADO DE LANGGRAPH (SHARED WORKSPACE) ---


class IntelligenceState(TypedDict):
    """Memoria de trabajo compartida entre los agentes del sistema."""

    query: str
    messages: Annotated[List[BaseMessage], add_messages]
    research_data: Optional[Dict[str, Any]]
    analysis_data: Optional[Dict[str, Any]]
    review_data: Optional[Dict[str, Any]]
    final_summary: Optional[str]
    hitl_pending: bool
    hitl_approved: Optional[bool]
    hitl_feedback: Optional[str]
    iteration_count: int
    next_agent: Literal[
        "Investigador", "Analista", "Revisor", "HITL", "FINALIZAR"
    ]
    session_id: str
