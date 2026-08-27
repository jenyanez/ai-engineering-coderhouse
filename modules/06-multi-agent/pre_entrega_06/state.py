"""Esquema de estado global y modelos de validación Pydantic para el Orquestador Multi-Agente."""

from typing import Annotated, List, Literal, Optional, TypedDict
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

# Nombres válidos de los nodos a los que puede enrutar el Supervisor
NextAgent = Literal["Investigador", "Analista", "FINALIZAR"]


class ResearchArtifact(BaseModel):
    """Contrato estructurado para los hallazgos producidos por el Agente de Investigación."""
    topic: str = Field(..., min_length=2, description="Tema o tecnología investigada")
    summary: str = Field(..., min_length=10, description="Síntesis de los datos y hechos recolectados")
    key_metrics: List[str] = Field(default_factory=list, description="Métricas o cifras encontradas")
    sources: List[str] = Field(default_factory=list, description="Fuentes o referencias consultadas")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Nivel de certeza de los datos (0 a 1)")


class AnalysisArtifact(BaseModel):
    """Contrato estructurado para el procesamiento cuantitativo del Agente de Análisis."""
    analysis_type: str = Field(..., description="Tipo de análisis realizado (ej. CAGR, Proyección, Comparativa)")
    calculated_metrics: str = Field(..., description="Resultados numéricos y cálculos cuantitativos")
    interpretation: str = Field(..., min_length=10, description="Interpretación técnica de los resultados")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones basadas en los datos")


class RouterDecision(BaseModel):
    """Esquema de decisión emitido por el Supervisor para enrutar el flujo."""
    next_agent: NextAgent = Field(
        ..., 
        description="Siguiente nodo a ejecutar: 'Investigador', 'Analista' o 'FINALIZAR'."
    )
    reasoning: str = Field(
        ..., 
        description="Justificación detallada de por qué se toma esta decisión de ruteo."
    )
    is_sufficient: bool = Field(
        default=False, 
        description="Indica si la información recolectada ya es suficiente para dar la respuesta final."
    )


class AgentState(TypedDict):
    """Estado global compartido entre el supervisor y los agentes especialistas."""
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: NextAgent
    research_data: Optional[dict]
    analysis_data: Optional[dict]
    final_summary: Optional[str]
    iteration_count: int
    error: Optional[str]
