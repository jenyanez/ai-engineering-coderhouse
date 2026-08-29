"""Módulo FinOps para cálculo y auditoría de costos de tokens en tiempo real."""

from typing import Dict, Optional


class FinOpsAuditor:
    """Calculador de costos de inferencia basado en tarificación oficial OpenAI."""

    # Tarifas por 1M de tokens (gpt-4o-mini & text-embedding-3-small)
    PRICE_PER_1M_INPUT_USD: float = 0.150
    PRICE_PER_1M_OUTPUT_USD: float = 0.600
    PRICE_PER_1M_EMBEDDINGS_USD: float = 0.020

    @classmethod
    def estimate_task_cost(
        cls,
        query: str,
        research_tokens: int = 1200,
        analysis_tokens: int = 800,
        synthesis_tokens: int = 1500,
        was_rejected: bool = False,
    ) -> Dict[str, float]:
        """Calcula el costo en USD y los ahorros generados por la tarea."""
        # Tokens aproximados consumidos por el pipeline
        input_tokens = len(query.split()) * 4 + 450 + (research_tokens if not was_rejected else 600)
        output_tokens = 250 if was_rejected else (synthesis_tokens + 350)
        total_tokens = input_tokens + output_tokens

        cost_input = (input_tokens / 1_000_000) * cls.PRICE_PER_1M_INPUT_USD
        cost_output = (output_tokens / 1_000_000) * cls.PRICE_PER_1M_OUTPUT_USD
        total_cost_usd = round(cost_input + cost_output, 6)

        # Ahorro si fue rechazado en HITL
        savings_usd = round((synthesis_tokens / 1_000_000) * cls.PRICE_PER_1M_OUTPUT_USD, 6) if was_rejected else 0.0

        return {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens,
            "estimated_cost_usd": total_cost_usd,
            "savings_usd": savings_usd,
        }
