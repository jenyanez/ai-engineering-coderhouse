"""Agente especialista en investigación profunda, extracción de mercado y consulta técnica."""

import os
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from state import AgentState, ResearchArtifact
from tools.search_tools import query_tech_knowledge_base, search_market_trends


def get_research_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0
    )


RESEARCH_SYSTEM_PROMPT = """Eres el Agente Especialista en Investigación y Extracción de Mercado.
Tu misión es consultar tus herramientas para extraer datos fácticos, métricas cuantitativas de mercado y fuentes confiables sobre la consulta del usuario.

Herramientas disponibles:
- `search_market_trends`: Consulta tamaño de mercado, proyecciones y tasas de adopción.
- `query_tech_knowledge_base`: Consulta mejores prácticas, drivers y riesgos técnicos.

Instrucciones:
1. Analiza el tema solicitado por el usuario.
2. Consulta tus herramientas para recopilar datos duros (valores iniciales, proyecciones y años).
3. Sintetiza los hallazgos en un informe claro y estructurado."""


def research_node(state: AgentState) -> dict:
    """Nodo especialista de investigación. Invoca herramientas y produce un ResearchArtifact."""
    llm = get_research_llm()
    tools = [search_market_trends, query_tech_knowledge_base]
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", RESEARCH_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    try:
        # 1. Invocación del agente para seleccionar y ejecutar herramientas
        chain = prompt | llm_with_tools
        response = chain.invoke({"messages": state["messages"]})
        
        tool_results = []
        if response.tool_calls:
            for tool_call in response.tool_calls:
                tool_name = tool_call["name"]
                tool_args = tool_call["args"]
                if tool_name == "search_market_trends":
                    res = search_market_trends.invoke(tool_args)
                    tool_results.append(f"Resultados de Mercado: {res}")
                elif tool_name == "query_tech_knowledge_base":
                    res = query_tech_knowledge_base.invoke(tool_args)
                    tool_results.append(f"Base Técnica: {res}")
        else:
            user_msg = state["messages"][0].content
            res = search_market_trends.invoke({"query": user_msg})
            tool_results.append(f"Resultados de Mercado: {res}")

        combined_context = "\n".join(tool_results)
        
        # 2. Estructuración y validación del artefacto mediante Pydantic
        structured_llm = llm.with_structured_output(ResearchArtifact, method="function_calling")
        struct_prompt = ChatPromptTemplate.from_messages([
            ("system", "Genera un ResearchArtifact estructurado a partir del siguiente contexto de investigación:"),
            ("human", "Contexto obtenido de herramientas:\n{context}")
        ])
        
        artifact: ResearchArtifact = (struct_prompt | structured_llm).invoke({"context": combined_context})
        
        msg_content = (
            f"🔍 [Investigación Completada]\n"
            f"• Tema: {artifact.topic}\n"
            f"• Síntesis: {artifact.summary}\n"
            f"• Métricas: {', '.join(artifact.key_metrics) if artifact.key_metrics else 'Consultadas'}\n"
            f"• Fuentes: {', '.join(artifact.sources)}\n"
            f"• Nivel de Confianza: {artifact.confidence_score * 100:.1f}%"
        )
        
        return {
            "messages": [HumanMessage(content=msg_content, name="Investigador")],
            "research_data": artifact.model_dump(),
            "error": None
        }
        
    except Exception as exc:
        return {
            "messages": [HumanMessage(content=f"Error en investigación: {str(exc)}", name="Investigador")],
            "error": f"ResearchNodeError: {str(exc)}"
        }
