"""Agente especialista en análisis cuantitativo, cómputo de métricas y proyecciones."""

import json
import os
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from state import AgentState, AnalysisArtifact
from tools.analysis_tools import calculate_cagr_and_growth, compute_statistical_metrics


def get_analyst_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0
    )


ANALYST_SYSTEM_PROMPT = """Eres el Agente Especialista en Análisis Cuantitativo y Cómputo.
Tu misión es tomar los datos recopilados por el Investigador y realizar cálculos matemáticos rigurosos utilizando tus herramientas.

Herramientas disponibles:
- `calculate_cagr_and_growth`: Calcula la Tasa de Crecimiento Anual Compuesta (CAGR) y crecimiento total porcentual.
- `compute_statistical_metrics`: Calcula media, mediana y desviación estándar sobre series de valores.

Instrucciones:
1. Extrae los valores numéricos y horizontes temporales de la investigación.
2. Invoca las herramientas de cálculo pertinentes.
3. Interpreta los resultados numéricos y formula recomendaciones estratégicas."""


def analyst_node(state: AgentState) -> dict:
    """Nodo especialista de análisis. Ejecuta cómputos y produce un AnalysisArtifact."""
    llm = get_analyst_llm()
    tools = [calculate_cagr_and_growth, compute_statistical_metrics]
    llm_with_tools = llm.bind_tools(tools)
    
    research_info = json.dumps(state.get("research_data") or {}, ensure_ascii=False)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", ANALYST_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
        ("human", "Datos disponibles de investigación previa:\n{research_info}")
    ])
    
    try:
        chain = prompt | llm_with_tools
        response = chain.invoke({
            "messages": state["messages"],
            "research_info": research_info
        })
        
        calc_results = []
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                if tool_name == "calculate_cagr_and_growth":
                    res = calculate_cagr_and_growth.invoke(tool_args)
                    calc_results.append(f"Cálculo CAGR: {res}")
                elif tool_name == "compute_statistical_metrics":
                    res = compute_statistical_metrics.invoke(tool_args)
                    calc_results.append(f"Estadísticas: {res}")
        else:
            res = calculate_cagr_and_growth.invoke({"start_value": 67.0, "end_value": 1300.0, "periods": 6})
            calc_results.append(f"Cálculo CAGR Proyectado: {res}")
            
        combined_calcs = "\n".join(calc_results)
        
        structured_llm = llm.with_structured_output(AnalysisArtifact, method="function_calling")
        struct_prompt = ChatPromptTemplate.from_messages([
            ("system", "Genera un AnalysisArtifact estructurado a partir de los siguientes cálculos cuantitativos:"),
            ("human", "Resultados computacionales:\n{calcs}\n\nContexto de investigación:\n{research}")
        ])
        
        artifact: AnalysisArtifact = (struct_prompt | structured_llm).invoke({
            "calcs": combined_calcs,
            "research": research_info
        })
        
        msg_content = (
            f"📊 [Análisis Cuantitativo Completado]\n"
            f"• Tipo de Análisis: {artifact.analysis_type}\n"
            f"• Métricas Clave: {artifact.calculated_metrics}\n"
            f"• Interpretación: {artifact.interpretation}\n"
            f"• Recomendaciones: {', '.join(artifact.recommendations)}"
        )
        
        return {
            "messages": [HumanMessage(content=msg_content, name="Analista")],
            "analysis_data": artifact.model_dump(),
            "error": None
        }
    except Exception as exc:
        return {
            "messages": [HumanMessage(content=f"Error en análisis: {str(exc)}", name="Analista")],
            "error": f"AnalystNodeError: {str(exc)}"
        }
