"""Nodo especialista de Abstención Segura y Mitigación de Alucinaciones."""

from langchain_core.messages import AIMessage
from state import AgentState


def abstention_node(state: AgentState) -> dict:
    """Nodo final de abstención segura. Emite una respuesta controlada sin alucinaciones."""
    report = state.get("abstention_report") or {}
    query_text = state["messages"][0].content if state.get("messages") else "Consulta"
    
    score = report.get("max_relevance_score", 0.0)
    thresh = report.get("threshold_applied", 0.65)
    
    response_text = (
        f"🛑 **INFORME DE ABSTENCIÓN TÉCNICA Y PROTECCIÓN DE GROUNDING**\n\n"
        f"• **Consulta Solicitada:** \"{query_text}\"\n"
        f"• **Diagnóstico de Retrieval:** La búsqueda semántica en la base vectorial no halló evidencias suficientes.\n"
        f"• **Puntaje de Similitud Máximo:** `{score:.4f}` (Umbral de certeza requerido: `{thresh:.2f}`).\n"
        f"• **Acción del Guardrail:** **Abstención Preventiva** activada de forma determinista por el Supervisor.\n\n"
        f"**Decisión Arquitectónica:**\n"
        f"El sistema bloqueó el cómputo de métricas y la síntesis generativa para evitar la propagación de alucinaciones o cifras inventadas en producción."
    )
    
    return {
        "messages": [AIMessage(content=response_text, name="AbstenciónSegura")],
        "final_summary": response_text
    }
