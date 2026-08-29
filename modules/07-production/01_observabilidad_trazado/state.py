"""Esquema de estado global y contratos Pydantic para el Orquestador Instrumentado."""

from typing import Annotated, List, Literal, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

NextAgent = Literal["Investigador", "Analista", "FINALIZAR", "ABSTENERSE"]


class ResearchArtifact(BaseModel):
    """Contrato estructurado para los hallazgos de investigación documental."""
    topic: str = Field(..., min_length=2, description="Tema investigado")
    summary: str = Field(..., min_length=10, description="Síntesis fáctica de los hallazgos")
    key_metrics: List[str] = Field(default_factory=list, description="Métricas cuantitativas extraídas")
    sources: List[str] = Field(default_factory=list, description="Documentos consultados en ChromaDB")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Nivel de certeza (0 a 1)")
    is_grounded: bool = Field(default=True, description="Indica si la evidencia supera el umbral de similitud")
    abstention_reason: Optional[str] = Field(default=None, description="Motivo técnico si se activa abstención")


class AnalysisArtifact(BaseModel):
    """Contrato estructurado para el cómputo cuantitativo y métricas estadísticas."""
    analysis_type: str = Field(..., description="Tipo de análisis (ej. CAGR, Proyecciones, Comparativa)")
    calculated_metrics: str = Field(..., description="Resultados numéricos exactos calculados")
    interpretation: str = Field(..., min_length=10, description="Interpretación técnica de los datos")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones estratégicas")


class RouterDecision(BaseModel):
    """Decisión de ruteo y compuerta de calidad emitida por el Supervisor."""
    next_agent: NextAgent = Field(..., description="Siguiente nodo: 'Investigador', 'Analista', 'FINALIZAR' o 'ABSTENERSE'")
    reasoning: str = Field(..., description="Justificación técnica de la delegación")
    is_sufficient: bool = Field(default=False, description="Indica si la información es suficiente para sintetizar")


class AgentState(TypedDict):
    """Estado compartido entre el supervisor y los agentes especialistas."""
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: NextAgent
    research_data: Optional[dict]
    analysis_data: Optional[dict]
    final_summary: Optional[str]
    iteration_count: int
    is_grounded: bool
    abstention_report: Optional[dict]
    error: Optional[str]
