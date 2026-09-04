"""Agente Analista especializado en razonamiento cuantitativo y métricas."""

from typing import Any, Dict
from langchain_core.messages import AIMessage
from app.core.state import AnalysisPayload, IntelligenceState
from app.observability.tracer import trace_agent_span
from app.tools.compute_tool import calculate_cagr


@trace_agent_span("analista", span_kind="agent")
def analyst_node(state: IntelligenceState) -> Dict[str, Any]:
    """Procesa los datos cuantitativos y genera proyecciones matemáticas."""
    research = state.get("research_data", {})

    if not research.get("found_in_kb", False):
        payload = AnalysisPayload(
            valid_analysis=False,
            interpretation="No aplica análisis cuantitativo para consultas fuera de dominio.",
        )
        return {
            "analysis_data": payload.model_dump(),
            "messages": [AIMessage(content="[Analista] Omitiendo cómputo por falta de datos.")],
        }

    val_start = research.get("market_size_2024_usd_b", 67.0) or 67.0
    val_end = research.get("market_size_2030_usd_b", 1300.0) or 1300.0
    cagr_result = calculate_cagr.invoke({
        "val_start": float(val_start),
        "val_end": float(val_end),
        "years": 6,
    })

    payload = AnalysisPayload(
        valid_analysis=cagr_result.get("valid_analysis", True),
        cagr_percentage=cagr_result.get("cagr_percentage"),
        expansion_factor=cagr_result.get("expansion_factor"),
        interpretation=cagr_result.get("interpretation", "Proyección calculada."),
    )

    msg = AIMessage(
        content=(
            f"[Analista] Análisis cuantitativo completado: CAGR del "
            f"{payload.cagr_percentage}% (Expansión de {payload.expansion_factor}x)."
        )
    )

    return {
        "analysis_data": payload.model_dump(),
        "messages": [msg],
    }
