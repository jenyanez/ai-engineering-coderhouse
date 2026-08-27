"""Nodo Supervisor: Orquestador jerárquico, router dinámico y compuerta de calidad."""

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


SUPERVISOR_SYSTEM_PROMPT = """Eres el Supervisor Orquestador de un sistema multi-agente jerárquico.
Tu función es coordinar la interacción entre dos especialistas:
1. 'Investigador': Encargado de buscar y extraer datos fácticos, tendencias y fuentes.
2. 'Analista': Encargado de computar métricas, CAGR y análisis cuantitativo sobre los datos investigados.

Rúbrica estricta de evaluación y suficiencia:
- Si el usuario solicita un análisis y aún NO se han obtenido datos del 'Investigador', delega a 'Investigador'.
- Si el 'Investigador' ya aportó datos pero aún NO han sido procesados por el 'Analista', delega a 'Analista'.
- Si tanto el 'Investigador' como el 'Analista' han completado sus tareas y la información es suficiente, responde 'FINALIZAR'.
- Si algún especialista cometió un error o faltan datos críticos, puedes solicitar una refinación indicando el especialista correspondiente.

Dada la conversación actual, decide exactamente el siguiente paso."""


def supervisor_node(state: AgentState) -> dict:
    """Nodo Supervisor: Evalúa el estado del grafo y emite la decisión de ruteo."""
    current_iterations = state.get("iteration_count", 0) + 1
    
    # Guardrail Anti-Loop: Evitar bucle infinito si se supera el tope de iteraciones
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
        
    llm = get_supervisor_llm()
    structured_llm = llm.with_structured_output(RouterDecision, method="function_calling")
    
    research_done = bool(state.get("research_data"))
    analysis_done = bool(state.get("analysis_data"))
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SUPERVISOR_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
        (
            "system",
            f"Estado actual de artefactos: [Investigación lista: {research_done}] | [Análisis listo: {analysis_done}]. "
            "¿Quién debe actuar ahora? Selecciona exactamente uno de: ['Investigador', 'Analista', 'FINALIZAR']."
        )
    ])
    
    chain = prompt | structured_llm
    decision: RouterDecision = chain.invoke({"messages": state["messages"]})
    
    # Validación determinista: Si falta investigación forzar Investigador, si falta análisis forzar Analista
    final_decision = decision.next_agent
    if not research_done:
        final_decision = "Investigador"
    elif research_done and not analysis_done:
        final_decision = "Analista"
        
    return {
        "next_agent": final_decision,
        "iteration_count": current_iterations
    }
