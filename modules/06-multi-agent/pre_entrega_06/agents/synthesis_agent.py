"""Nodo de Síntesis Final: Consolida los hallazgos de investigación y análisis en un informe ejecutivo."""

import json
import os
from langchain_core.messages import AIMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI

from state import AgentState


def get_synthesis_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0.2
    )


SYNTHESIS_SYSTEM_PROMPT = """Eres el Redactor Ejecutivo en Jefe del sistema multi-agente.
Tu objetivo es elaborar la Síntesis Ejecutiva Final consolidando los datos aportados por los especialistas.

Estructura obligatoria del informe:
1. 📋 Resumen Ejecutivo y Hallazgos Principales (aportados por el Investigador).
2. 📊 Métricas Cuantitativas y Crecimiento/CAGR (aportados por el Analista).
3. 🎯 Conclusiones Estratégicas y Recomendaciones de Acción.

Asegúrate de que el tono sea profesional, directo y fundamentado en los datos recopilados."""


def synthesis_node(state: AgentState) -> dict:
    """Nodo final de consolidación y generación del informe ejecutivo."""
    llm = get_synthesis_llm()
    
    research_str = json.dumps(state.get("research_data") or {}, ensure_ascii=False, indent=2)
    analysis_str = json.dumps(state.get("analysis_data") or {}, ensure_ascii=False, indent=2)
    query_text = state["messages"][0].content if state.get("messages") else "Consulta general"
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYNTHESIS_SYSTEM_PROMPT),
        (
            "human",
            "Consulta del Usuario:\n{query}\n\n"
            "Datos del Investigador:\n{research}\n\n"
            "Datos del Analista:\n{analysis}\n\n"
            "Elabora la Síntesis Ejecutiva Final."
        )
    ])
    
    chain = prompt | llm
    response = chain.invoke({
        "query": query_text,
        "research": research_str,
        "analysis": analysis_str
    })
    
    summary_text = response.content
    
    return {
        "messages": [AIMessage(content=summary_text, name="Sintetizador")],
        "final_summary": summary_text
    }
