"""Módulo de gestión para el flujo Human-in-the-Loop (HITL)."""

import logging
from typing import Any, Dict, Optional

logger = logging.getLogger("HITL")


class HITLManager:
    """Controlador de intervención humana y reanudación de checkpoints."""

    @staticmethod
    def is_critical_operation(query: str, require_approval: bool) -> bool:
        """Determina si la tarea requiere pausa obligatoria antes de la síntesis."""
        if not require_approval:
            return False
        # Palabras clave de alto impacto o solicitud explícita
        critical_keywords = ["cagr", "inversión", "mercado", "riesgos", "costo", "proyección", "producción"]
        return any(kw in query.lower() for kw in critical_keywords) or len(query) > 10

    @staticmethod
    def format_intermediate_summary(research_data: Optional[Dict[str, Any]], analysis_data: Optional[Dict[str, Any]]) -> str:
        """Genera un resumen previo para la toma de decisión del supervisor humano."""
        r = research_data or {}
        a = analysis_data or {}
        return (
            f"Hallazgos: Mercado {r.get('market_size_2024_usd_b')}B -> {r.get('market_size_2030_usd_b')}B. "
            f"Análisis: CAGR {a.get('cagr_percentage')}%. ¿Autoriza emitir el informe ejecutivo final?"
        )
