"""Construcción y orquestación del StateGraph para el Orquestador Multi-Agente Jerárquico."""

from langgraph.graph import END, StateGraph

from agents import analyst_node, research_node, supervisor_node, synthesis_node
from state import AgentState


def build_orchestrator_graph():
    """Construye y compila el grafo multi-agente con topología jerárquica (Patrón Supervisor)."""
    builder = StateGraph(AgentState)

    # 1. Registro de nodos
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("Investigador", research_node)
    builder.add_node("Analista", analyst_node)
    builder.add_node("Sintetizador", synthesis_node)

    # 2. Punto de entrada central en el Supervisor
    builder.set_entry_point("supervisor")

    # 3. Aristas de retorno: los especialistas devuelven el control al Supervisor
    builder.add_edge("Investigador", "supervisor")
    builder.add_edge("Analista", "supervisor")

    # 4. Arista condicional: el Supervisor delega dinámicamente según next_agent
    builder.add_conditional_edges(
        "supervisor",
        lambda state: state["next_agent"],
        {
            "Investigador": "Investigador",
            "Analista": "Analista",
            "FINALIZAR": "Sintetizador"
        }
    )

    # 5. La síntesis ejecutiva conduce al cierre del flujo
    builder.add_edge("Sintetizador", END)

    return builder.compile()


# Instancia compilada del orquestador
graph = build_orchestrator_graph()
