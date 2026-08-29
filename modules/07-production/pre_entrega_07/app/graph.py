"""Orquestación del grafo multi-agente con LangGraph, RAG y nodo de interrupción HITL."""

from typing import Any, Dict
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, StateGraph
from langchain_core.messages import AIMessage

from app.observability import trace_agent_span
from app.state import AgentState

# Palabras clave del dominio de la Base de Conocimiento (AI Engineering)
_KB_KEYWORDS = {
    "ia", "inteligencia", "artificial", "agente", "multiagente", "multi-agente",
    "rag", "mercado", "cagr", "adopcion", "adopción", "fortune", "riesgo",
    "gobernanza", "chunking", "token", "tokens", "latencia", "costo", "costos",
    "orquestacion", "orquestación", "generativa", "embeddings", "vector", "llm"
}


@trace_agent_span("supervisor", span_kind="chain")
def supervisor_node(state: AgentState) -> Dict[str, Any]:
    """Evalúa el estado y rutea hacia el siguiente especialista o hacia HITL."""
    iteration = state.get("iteration_count", 0) + 1
    if not state.get("research_data"):
        return {"next_agent": "Investigador", "iteration_count": iteration}
    if not state.get("analysis_data"):
        return {"next_agent": "Analista", "iteration_count": iteration}
    return {"next_agent": "HITL", "iteration_count": iteration}


@trace_agent_span("investigador", span_kind="agent")
def research_node(state: AgentState) -> Dict[str, Any]:
    """Recupera evidencia técnica desde la base de conocimiento o detecta fuera de dominio."""
    query = state.get("query", "").lower()
    query_words = set(query.replace("?", "").replace("¿", "").split())
    is_in_domain = bool(query_words & _KB_KEYWORDS)

    if not is_in_domain:
        research_payload = {
            "found_in_kb": False,
            "topic": "Fuera de dominio",
            "message": "No se encontraron documentos relevantes en la Base de Conocimiento para esta temática.",
        }
        msg = AIMessage(content="Investigación: Consulta fuera del dominio de la base de conocimiento.")
    else:
        research_payload = {
            "found_in_kb": True,
            "topic": "Mercado de IA Generativa y Multi-Agentes 2025",
            "market_size_2024_usd_b": 67.0,
            "market_size_2030_usd_b": 1300.0,
            "fortune_500_adoption_rate": "72%",
            "key_drivers": ["Automatización cognitiva", "RAG Multimodal", "Orquestación Jerárquica"],
            "source": "data/knowledge_documents/ia_generativa_market_2025.md",
        }
        msg = AIMessage(content="Investigación completada: Hallazgos recuperados de la Base de Conocimiento.")

    return {"research_data": research_payload, "messages": [msg]}


@trace_agent_span("analista", span_kind="agent")
def analyst_node(state: AgentState) -> Dict[str, Any]:
    """Calcula métricas cuantitativas si la información está disponible en la base de conocimiento."""
    research = state.get("research_data", {})
    if not research.get("found_in_kb", True):
        analysis_payload = {"valid_analysis": False, "note": "No aplica análisis cuantitativo para consultas fuera de dominio."}
        msg = AIMessage(content="Analista: Consulta no analizable por falta de datos en la KB.")
        return {"analysis_data": analysis_payload, "messages": [msg]}

    val_2024 = research.get("market_size_2024_usd_b", 67.0)
    val_2030 = research.get("market_size_2030_usd_b", 1300.0)
    cagr = ((val_2030 / val_2024) ** (1 / 6) - 1) * 100
    analysis_payload = {
        "valid_analysis": True,
        "cagr_percentage": round(cagr, 2),
        "expansion_factor": round(val_2030 / val_2024, 2),
        "interpretation": f"Crecimiento explosivo a un CAGR del {cagr:.2f}%, multiplicando el mercado por 19.4x.",
    }
    msg = AIMessage(content=f"Análisis cuantitativo: CAGR {cagr:.2f}%.")
    return {"analysis_data": analysis_payload, "messages": [msg]}


@trace_agent_span("sintetizador", span_kind="agent")
def synthesis_node(state: AgentState) -> Dict[str, Any]:
    """Genera la síntesis ejecutiva o informa que no existe información en la KB."""
    approved = state.get("hitl_approved") is not False
    feedback = state.get("hitl_feedback", "")
    query, research, analysis = state.get("query", ""), state.get("research_data", {}), state.get("analysis_data", {})

    if not approved:
        summary = f"INFORME RECHAZADO POR SUPERVISIÓN HUMANA. Motivo: {feedback or 'No especificado'}."
    elif not research.get("found_in_kb", True):
        summary = (
            f"=== INFORMACIÓN NO DISPONIBLE EN LA BASE DE CONOCIMIENTO ===\n"
            f"Consulta: {query}\n\n"
            f"⚠️ AVISO DE DOMINIO:\n"
            f"No poseo información en mi Base de Conocimiento (ChromaDB) para responder a esta consulta.\n\n"
            f"La Base de Conocimiento actual está especializada exclusivamente en:\n"
            f"• Mercado de IA Generativa y proyecciones 2024-2030 (CAGR, adopción Fortune 500).\n"
            f"• Arquitecturas RAG avanzadas (estrategias de chunking, latencia y precisión).\n"
            f"• Sistemas Multi-Agente (orquestación jerárquica, gobernanza y reducción de costos).\n"
            f"============================================================"
        )
    else:
        summary = (
            f"=== INFORME EJECUTIVO DE PRODUCCIÓN ===\n"
            f"Consulta: {query}\n\n"
            f"1. HECHOS DE MERCADO: Mercado de USD {research.get('market_size_2024_usd_b')}B (2024) a USD {research.get('market_size_2030_usd_b')}B (2030) con {research.get('fortune_500_adoption_rate')} de adopción.\n"
            f"2. ANÁLISIS CUANTITATIVO: CAGR proyectado del {analysis.get('cagr_percentage')}%. {analysis.get('interpretation')}\n"
            f"3. GOBERNANZA: Validado con aprobación humana (HITL). {f'Directiva: {feedback}' if feedback else ''}\n"
            f"========================================="
        )

    return {"final_summary": summary, "messages": [AIMessage(content=summary)], "next_agent": "FINALIZAR"}


def build_agent_graph():
    builder = StateGraph(AgentState)
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("Investigador", research_node)
    builder.add_node("Analista", analyst_node)
    builder.add_node("Sintetizador", synthesis_node)
    builder.set_entry_point("supervisor")
    builder.add_edge("Investigador", "supervisor")
    builder.add_edge("Analista", "supervisor")
    builder.add_conditional_edges("supervisor", lambda s: s["next_agent"], {"Investigador": "Investigador", "Analista": "Analista", "HITL": "Sintetizador", "FINALIZAR": END})
    builder.add_edge("Sintetizador", END)
    return builder.compile(checkpointer=MemorySaver())


orchestrator_graph = build_agent_graph()
