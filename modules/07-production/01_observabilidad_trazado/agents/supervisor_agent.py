"""Nodo Supervisor: Orquestador jerárquico, router dinámico y compuerta de calidad con compuerta de abstención."""

import os
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from state import AgentState, RouterDecision

MAX_ITERATIONS = 6


def get_supervisor_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0
    )


SUPERVISOR_SYSTEM_PROMPT = """Eres el Supervisor Orquestador de un sistema multi-agente jerárquico con compuerta estricta de abstención.
Tu función es coordinar la interacción entre dos especialistas:
1. 'Investigador': Busca y extrae datos fácticos de ChromaDB y evalúa el anclaje documental.
2. 'Analista': Computa métricas, CAGR y análisis cuantitativo sobre los datos investigados.

Reglas estrictas de ruteo:
- Si el 'Investigador' determinó que la consulta NO está respaldada documentalmente (is_grounded == False), delega inmediatamente a 'ABSTENERSE'.
- Si aún NO se han obtenido datos del 'Investigador', delega a 'Investigador'.
- Si el 'Investigador' ya aportó datos grounded pero aún NO han sido procesados por el 'Analista', delega a 'Analista'.
- Si tanto el 'Investigador' como el 'Analista' han completado sus tareas con datos verificados, responde 'FINALIZAR'."""


def supervisor_node(state: AgentState) -> dict:
    """Nodo Supervisor: Evalúa el estado del grafo y emite la decisión de ruteo."""
    current_iterations = state.get("iteration_count", 0) + 1
    
    if current_iterations >= MAX_ITERATIONS:
        return {
            "next_agent": "FINALIZAR",
            "iteration_count": current_iterations,
            "messages": [
                AIMessage(
                    content="⚠️ Límite de iteraciones alcanzado por el Supervisor. Cerrando flujo para evitar bucle.",
                    name="Supervisor"
                )
            ]
        }
        
    # Compuerta determinista de abstención
    if state.get("is_grounded") is False:
        return {
            "next_agent": "ABSTENERSE",
            "iteration_count": current_iterations,
            "messages": [
                AIMessage(
                    content="🛑 [Compuerta de Calidad] El Investigador detectó falta de grounding documental. Ruteando al nodo de abstención segura para prevenir alucinaciones.",
                    name="Supervisor"
                )
            ]
        }

    research_done = bool(state.get("research_data"))
    analysis_done = bool(state.get("analysis_data"))
    
    if not research_done:
        final_decision = "Investigador"
    elif research_done and not analysis_done:
        final_decision = "Analista"
    else:
        final_decision = "FINALIZAR"
        
    return {
        "next_agent": final_decision,
        "iteration_count": current_iterations
    }
