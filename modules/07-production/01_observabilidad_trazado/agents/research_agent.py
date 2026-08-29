"""Agente especialista en investigación profunda, extracción de mercado y consulta a ChromaDB con guardrail de abstención."""

import json
import os
from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from abstention_guardrail import evaluate_grounding_and_abstention
from state import AgentState, ResearchArtifact
from tools.search_tools import query_chroma_vector_db, query_tech_knowledge_base, search_market_trends


def get_research_llm():
    return ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0
    )


RESEARCH_SYSTEM_PROMPT = """Eres el Agente Especialista en Investigación y Extracción de Mercado.
Tu misión es consultar tus herramientas para extraer datos fácticos y métricas de ChromaDB sobre la consulta del usuario.

Herramientas disponibles:
- `search_market_trends`: Consulta tamaño de mercado, proyecciones y adopción.
- `query_tech_knowledge_base`: Consulta mejores prácticas, drivers y riesgos técnicos.
- `query_chroma_vector_db`: Búsqueda semántica directa en la base vectorial.

Instrucciones:
1. Analiza el tema solicitado por el usuario y ejecuta las herramientas de búsqueda.
2. Si la información no existe o la relevancia es baja, reconócelo explícitamente."""


def research_node(state: AgentState) -> dict:
    """Nodo especialista de investigación. Evalúa grounding y produce un ResearchArtifact."""
    llm = get_research_llm()
    tools = [search_market_trends, query_tech_knowledge_base, query_chroma_vector_db]
    llm_with_tools = llm.bind_tools(tools)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", RESEARCH_SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])
    
    try:
        user_query = state["messages"][0].content
        raw_res = query_chroma_vector_db.invoke({"query": user_query, "k": 3})
        res_data = json.loads(raw_res) if isinstance(raw_res, str) else raw_res
        retrieved_chunks = res_data.get("chunks", []) if isinstance(res_data, dict) else []
        
        # 1. Evaluación del Guardrail Técnico de Grounding y Abstención
        abstention_report = evaluate_grounding_and_abstention(user_query, retrieved_chunks)
        
        if not abstention_report.is_grounded:
            # Protocolo de abstención técnica activado
            artifact = ResearchArtifact(
                topic=user_query,
                summary=abstention_report.safe_message,
                key_metrics=[],
                sources=[],
                confidence_score=abstention_report.max_relevance_score,
                is_grounded=False,
                abstention_reason=abstention_report.abstention_reason
            )
            msg_content = f"🛑 [Abstención Activada] {abstention_report.safe_message}"
            return {
                "messages": [HumanMessage(content=msg_content, name="Investigador")],
                "research_data": artifact.model_dump(),
                "is_grounded": False,
                "abstention_report": abstention_report.model_dump(),
                "error": None
            }

        # 2. Si la consulta tiene respaldo documental suficiente (is_grounded == True)
        combined_context = "\n".join([c.get("content", "") for c in retrieved_chunks])
        structured_llm = llm.with_structured_output(ResearchArtifact, method="function_calling")
        struct_prompt = ChatPromptTemplate.from_messages([
            ("system", "Genera un ResearchArtifact estructurado a partir del siguiente contexto de investigación fáctico:"),
            ("human", "Contexto obtenido de herramientas:\n{context}")
        ])
        
        artifact: ResearchArtifact = (struct_prompt | structured_llm).invoke({"context": combined_context})
        artifact.is_grounded = True
        artifact.confidence_score = abstention_report.max_relevance_score
        
        msg_content = (
            f"🔍 [Investigación Concluida - Grounded]\n"
            f"• Tema: {artifact.topic}\n"
            f"• Síntesis: {artifact.summary}\n"
            f"• Métricas: {', '.join(artifact.key_metrics) if artifact.key_metrics else 'Consultadas'}\n"
            f"• Fuentes: {', '.join(artifact.sources)}\n"
            f"• Certeza Semántica: {artifact.confidence_score * 100:.1f}%"
        )
        
        return {
            "messages": [HumanMessage(content=msg_content, name="Investigador")],
            "research_data": artifact.model_dump(),
            "is_grounded": True,
            "abstention_report": abstention_report.model_dump(),
            "error": None
        }
    except Exception as exc:
        return {
            "messages": [HumanMessage(content=f"Error en investigación: {str(exc)}", name="Investigador")],
            "is_grounded": False,
            "error": f"ResearchNodeError: {str(exc)}"
        }
