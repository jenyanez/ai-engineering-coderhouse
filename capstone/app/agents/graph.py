"""Construcción y compilación del grafo multi-agente con RedisCheckpointer."""

from typing import Any, Dict
from langgraph.graph import END, StateGraph
from app.agents.analyst import analyst_node
from app.agents.researcher import research_node
from app.agents.reviewer import reviewer_node
from app.agents.supervisor import supervisor_node
from app.config import settings
from app.core.checkpointer import RedisCheckpointer
from app.core.state import IntelligenceState


def hitl_pause_node(state: IntelligenceState) -> Dict[str, Any]:
    """Punto de interrupción que suspende el grafo a la espera de veredicto humano."""
    return {"hitl_pending": True, "next_agent": "HITL"}


def build_intelligence_graph(checkpointer: Any = None):
    """Construye y compila el flujo orquestado con patrón Supervisor."""
    builder = StateGraph(IntelligenceState)

    # Registro de nodos
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("Investigador", research_node)
    builder.add_node("Analista", analyst_node)
    builder.add_node("Revisor", reviewer_node)
    builder.add_node("HITL", hitl_pause_node)

    # Punto de entrada
    builder.set_entry_point("supervisor")

    # Retorno de especialistas al supervisor
    builder.add_edge("Investigador", "supervisor")
    builder.add_edge("Analista", "supervisor")
    builder.add_edge("Revisor", "supervisor")
    builder.add_edge("HITL", END)

    # Aristas condicionales dinámicas desde el supervisor
    builder.add_conditional_edges(
        "supervisor",
        lambda state: state["next_agent"],
        {
            "Investigador": "Investigador",
            "Analista": "Analista",
            "Revisor": "Revisor",
            "HITL": "HITL",
            "FINALIZAR": END,
        },
    )

    if checkpointer is None:
        try:
            from app.api.store import task_store

            sync_client = task_store.get_sync_client()
            checkpointer = RedisCheckpointer(
                sync_client, prefix=settings.redis_checkpoint_prefix
            )
        except Exception:
            from langgraph.checkpoint.memory import MemorySaver

            checkpointer = MemorySaver()

    return builder.compile(checkpointer=checkpointer)


# Instancia compilada global del grafo
intelligence_graph = build_intelligence_graph()
