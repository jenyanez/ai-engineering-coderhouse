"""
Pre-entrega 5: Agente de Razonamiento Cíclico con Memoria Persistente
Archivo: graph.py — Fase 2: StateGraph, Nodos y Ciclo ReAct

Construye el grafo del agente con:
- MessagesState como esquema de estado (historial acumulativo).
- ChatOpenAI vinculado a herramientas via bind_tools().
- Ciclo ReAct: agent → tools_condition → ToolNode → agent.
- AsyncSqliteSaver como checkpointer para persistencia.
"""

import os
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langgraph.graph import StateGraph, MessagesState, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from langgraph.checkpoint.sqlite.aio import AsyncSqliteSaver

from tools import tools_list

# Cargar variables de entorno
load_dotenv()


def _build_model() -> ChatOpenAI:
    """Instancia el LLM y vincula las herramientas disponibles."""
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0,
    )
    return llm.bind_tools(tools_list)


# Modelo con herramientas vinculadas (module-level para reutilización)
model_with_tools = _build_model()


async def call_model(state: MessagesState) -> dict:
    """
    Nodo 'agent': Invoca al LLM con el historial acumulado.
    El modelo decide autónomamente si necesita una herramienta
    o si ya puede generar la respuesta final.
    """
    response = await model_with_tools.ainvoke(state["messages"])
    return {"messages": [response]}


def create_agent_graph(checkpointer: AsyncSqliteSaver):
    """
    Construye, conecta y compila el StateGraph del agente ReAct.

    Args:
        checkpointer: Instancia de AsyncSqliteSaver para persistencia.

    Flujo:
    1. START → 'agent' (el LLM analiza el mensaje)
    2. 'agent' → tools_condition:
       - Si hay tool_calls → 'tools' (ToolNode ejecuta la herramienta)
       - Si no hay tool_calls → END (respuesta final)
    3. 'tools' → 'agent' (resultado de la herramienta regresa al LLM)
    """
    # 1. Inicializar el grafo con MessagesState
    workflow = StateGraph(MessagesState)

    # 2. Registrar nodos
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", ToolNode(tools_list))

    # 3. Definir aristas
    workflow.add_edge(START, "agent")
    workflow.add_conditional_edges("agent", tools_condition)
    workflow.add_edge("tools", "agent")

    # 4. Compilar con checkpointer
    return workflow.compile(checkpointer=checkpointer)
