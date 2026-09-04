"""Nodo Supervisor: Orquestador jerárquico y director de flujo del sistema."""

from typing import Any, Dict
from langchain_core.messages import AIMessage
from app.core.state import IntelligenceState
from app.observability.tracer import trace_agent_span


@trace_agent_span("supervisor", span_kind="chain")
def supervisor_node(state: IntelligenceState) -> Dict[str, Any]:
    """Analiza la memoria compartida y determina el siguiente paso operativo."""
    iteration = state.get("iteration_count", 0) + 1

    # Paso 1: Si no hay investigación, delegar al Investigador RAG
    if not state.get("research_data"):
        return {
            "next_agent": "Investigador",
            "iteration_count": iteration,
            "messages": [AIMessage(content="[Supervisor] Delegando tarea al Investigador RAG.")],
        }

    research = state["research_data"]

    # Paso 2: Si la consulta está fuera de dominio, enviar directo a Revisor para emitir abstención
    if not research.get("found_in_kb", True):
        return {
            "next_agent": "Revisor",
            "iteration_count": iteration,
            "messages": [AIMessage(content="[Supervisor] Consulta fuera de dominio. Derivando a Revisor.")],
        }

    # Paso 3: Evaluar si la consulta requiere análisis cuantitativo
    query = state.get("query", "").lower()
    needs_quant = bool(research.get("market_size_2024_usd_b")) or any(
        w in query for w in ["cagr", "calcul", "crecimiento", "proyecc", "tasa", "mercado", "usd"]
    )
    if needs_quant and not state.get("analysis_data"):
        return {
            "next_agent": "Analista",
            "iteration_count": iteration,
            "messages": [AIMessage(content="[Supervisor] Delegando métricas cuantitativas al Analista.")],
        }

    # Paso 4: Si falta la auditoría de calidad, delegar al Revisor
    if not state.get("review_data"):
        return {
            "next_agent": "Revisor",
            "iteration_count": iteration,
            "messages": [AIMessage(content="[Supervisor] Derivando reporte consolidado al Revisor.")],
        }

    review = state["review_data"]

    # Paso 5: Si el revisor determinó criticidad y requiere HITL y no se ha resuelto
    if review.get("requires_hitl", False) and state.get("hitl_approved") is None:
        return {
            "next_agent": "HITL",
            "hitl_pending": True,
            "iteration_count": iteration,
            "messages": [AIMessage(content="[Supervisor] Pausando ejecución: Requiere intervención humana.")],
        }

    # Paso 6: Flujo completado satisfactoriamente
    return {
        "next_agent": "FINALIZAR",
        "hitl_pending": False,
        "iteration_count": iteration,
        "messages": [AIMessage(content="[Supervisor] Tarea concluida. Reporte final listo.")],
    }
