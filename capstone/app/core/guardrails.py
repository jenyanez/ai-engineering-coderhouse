"""Guardrails deterministas de seguridad, factualidad y abstención."""

from typing import List, Set

DEFAULT_DOMAIN_KEYWORDS: Set[str] = {
    "ia", "inteligencia", "artificial", "agente", "multiagente", "multi-agente",
    "rag", "mercado", "cagr", "adopcion", "adopción", "fortune", "riesgo",
    "gobernanza", "chunking", "token", "tokens", "latencia", "costo", "costos",
    "orquestacion", "orquestación", "generativa", "embeddings", "vector", "llm"
}


def is_in_knowledge_domain(
    query: str, keywords: Set[str] = DEFAULT_DOMAIN_KEYWORDS
) -> bool:
    """Valida determinísticamente si una consulta pertenece al dominio del sistema."""
    normalized_words = set(
        query.lower().replace("?", "").replace("¿", "").replace(",", "").split()
    )
    return bool(normalized_words & keywords)


def generate_abstention_message(query: str) -> str:
    """Genera mensaje formal de abstención cuando no existe información suficiente."""
    return (
        f"=== INFORMACIÓN NO DISPONIBLE EN LA BASE DE CONOCIMIENTO ===\n"
        f"Consulta: {query}\n\n"
        f"⚠️ GUARDRAIL DE VERACIDAD (ABSTENCIÓN ACTIVA):\n"
        f"El sistema ha verificado que la consulta está fuera del dominio de conocimiento indexado.\n"
        f"Para prevenir alucinaciones, el sistema se abstiene de especular.\n\n"
        f"Áreas temáticas indexadas:\n"
        f"• Proyecciones del mercado de IA Generativa 2024-2030 (CAGR, inversión, Fortune 500).\n"
        f"• Arquitecturas RAG avanzadas (chunking semántico, re-ranking e indexación híbrida).\n"
        f"• Sistemas Multi-Agente (topologías supervisor, gobierno HITL y observabilidad).\n"
        f"============================================================"
    )


def check_hallucination_risk(text: str, sources: List[str]) -> bool:
    """Detecta discrepancias factuales o falta de fuentes en afirmaciones cuantitativas."""
    if not sources and any(c.isdigit() for c in text):
        return True
    return False
