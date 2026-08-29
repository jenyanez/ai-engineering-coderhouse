"""Construcción y compilación del StateGraph con instrumentación y guardrail de abstención."""

from langgraph.graph import END, StateGraph
from agents import analyst_node, research_node, supervisor_node, synthesis_node, abstention_node
from state import AgentState
from tracer_setup import init_tracing

# Activar trazabilidad global antes de compilar el grafo
init_tracing()


def build_orchestrator_graph():
    """Construye y compila el grafo multi-agente con topología jerárquica y compuerta de abstención."""
    builder = StateGraph(AgentState)

    # 1. Registro de nodos
    builder.add_node("supervisor", supervisor_node)
    builder.add_node("Investigador", research_node)
    builder.add_node("Analista", analyst_node)
    builder.add_node("Sintetizador", synthesis_node)
    builder.add_node("Abstención", abstention_node)

    # 2. Punto de entrada
    builder.set_entry_point("supervisor")

    # 3. Aristas de retorno
    builder.add_edge("Investigador", "supervisor")
    builder.add_edge("Analista", "supervisor")

    # 4. Aristas condicionales con compuerta de abstención
    builder.add_conditional_edges(
        "supervisor",
        lambda state: state["next_agent"],
        {
            "Investigador": "Investigador",
            "Analista": "Analista",
            "FINALIZAR": "Sintetizador",
            "ABSTENERSE": "Abstención"
        }
    )

    # 5. Cierres del grafo
    builder.add_edge("Sintetizador", END)
    builder.add_edge("Abstención", END)

    return builder.compile()


# Grafo compilado e instrumentado
graph = build_orchestrator_graph()
