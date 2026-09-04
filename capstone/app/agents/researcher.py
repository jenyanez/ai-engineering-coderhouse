"""Agente Investigador especializado en recuperación semántica y evidencia RAG."""

from typing import Any, Dict
from langchain_core.messages import AIMessage
from app.core.state import IntelligenceState, ResearchPayload
from app.observability.tracer import trace_agent_span
from app.tools.rag_tool import search_knowledge_base


@trace_agent_span("investigador", span_kind="agent")
def research_node(state: IntelligenceState) -> Dict[str, Any]:
    """Ejecuta la recuperación documental y valida la evidencia encontrada."""
    query = state.get("query", "")
    raw_results = search_knowledge_base.invoke({"query": query, "top_k": 3})

    # Validación mediante modelo Pydantic
    payload = ResearchPayload(
        found_in_kb=raw_results.get("found_in_kb", False),
        topic=raw_results.get("topic", "Sin tema"),
        market_size_2024_usd_b=raw_results.get("market_size_2024_usd_b"),
        market_size_2030_usd_b=raw_results.get("market_size_2030_usd_b"),
        fortune_500_adoption_rate=raw_results.get("fortune_500_adoption_rate"),
        key_drivers=raw_results.get("key_drivers", []),
        source=raw_results.get("source", "Base documental"),
        evidence_snippet=raw_results.get("evidence_snippet", ""),
    )

    if not payload.found_in_kb:
        msg = AIMessage(
            content="[Investigador] La consulta está fuera de la Base de Conocimiento indexada."
        )
    else:
        msg = AIMessage(
            content=(
                f"[Investigador] Hallazgos recuperados de '{payload.source}'. "
                f"Tema: {payload.topic}."
            )
        )

    return {
        "research_data": payload.model_dump(),
        "messages": [msg],
    }
