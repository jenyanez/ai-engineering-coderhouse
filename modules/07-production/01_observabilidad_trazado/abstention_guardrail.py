"""Módulo de Guardrail de Grounding y Criterio de Abstención Explícito."""

from typing import List, Optional
from pydantic import BaseModel, Field
from opentelemetry import trace

# Obtener tracer para emitir spans explícitos del guardrail
tracer = trace.get_tracer("grounding_guardrail")

# Umbral calibrado de similitud semántica para validar grounding fáctico
SIMILARITY_THRESHOLD = 0.22


class AbstentionReport(BaseModel):
    """Contrato del reporte de abstención generado cuando la relevancia es insuficiente."""
    is_grounded: bool = Field(..., description="Indica si la consulta cuenta con respaldo documental suficiente")
    max_relevance_score: float = Field(..., description="Puntaje máximo de similitud encontrado")
    threshold_applied: float = Field(default=SIMILARITY_THRESHOLD, description="Umbral exigido")
    status: str = Field(..., description="Estado de evaluación: 'GROUNDED' o 'ABSTAINED'")
    action_taken: str = Field(..., description="Acción tomada: 'PROCEED' o 'SAFE_REFUSAL'")
    abstention_reason: Optional[str] = Field(default=None, description="Motivo técnico de la abstención")
    safe_message: str = Field(..., description="Mensaje seguro de degradación para el usuario")


def evaluate_grounding_and_abstention(query: str, retrieved_chunks: List[dict]) -> AbstentionReport:
    """Evalúa la relevancia de los fragmentos recuperados y emite un span de telemetría."""
    with tracer.start_as_current_span("guardrail.grounding_evaluation") as span:
        scores = [chunk.get("relevance_score", 0.0) for chunk in retrieved_chunks]
        max_score = max(scores) if scores else 0.0
        
        span.set_attribute("guardrail.query", query)
        span.set_attribute("guardrail.threshold", SIMILARITY_THRESHOLD)
        span.set_attribute("guardrail.max_relevance_score", max_score)
        span.set_attribute("guardrail.total_chunks", len(retrieved_chunks))

        if not retrieved_chunks or max_score < SIMILARITY_THRESHOLD:
            # Condición de abstención técnica activada (< 0.22)
            span.set_attribute("guardrail.grounded", False)
            span.set_attribute("guardrail.action", "ABSTAIN")
            
            report = AbstentionReport(
                is_grounded=False,
                max_relevance_score=round(max_score, 4),
                threshold_applied=SIMILARITY_THRESHOLD,
                status="ABSTAINED",
                action_taken="SAFE_REFUSAL",
                abstention_reason=(
                    f"La similitud máxima ({max_score:.4f}) está por debajo del umbral de anclaje ({SIMILARITY_THRESHOLD}). "
                    "Se activa el protocolo de abstención para prevenir alucinaciones."
                ),
                safe_message=(
                    f"⚠️ [Protocolo de Abstención Activado]\n"
                    f"No se encontraron evidencias documentales suficientes en la base de conocimiento para responder: '{query}'. "
                    f"Similitud semántica observada: {max_score:.4f} (umbral requerido: {SIMILARITY_THRESHOLD}).\n"
                    f"Para preservar la precisión factual, el sistema se abstiene de especular o calcular proyecciones sin datos verificables."
                )
            )
        else:
            # Condición de grounding superada (>= 0.22)
            span.set_attribute("guardrail.grounded", True)
            span.set_attribute("guardrail.action", "PROCEED")
            
            report = AbstentionReport(
                is_grounded=True,
                max_relevance_score=round(max_score, 4),
                threshold_applied=SIMILARITY_THRESHOLD,
                status="GROUNDED",
                action_taken="PROCEED",
                abstention_reason=None,
                safe_message="Consulta con suficiente respaldo factual en ChromaDB."
            )
            
        return report
