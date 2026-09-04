"""Cálculo de tokens consumidos y estimación de costos FinOps para LLMs."""

from typing import Dict

# Precios oficiales por 1M tokens (USD)
MODEL_PRICING: Dict[str, Dict[str, float]] = {
    "gpt-4o-mini": {"prompt": 0.15, "completion": 0.60},
    "gpt-4o": {"prompt": 2.50, "completion": 10.00},
    "text-embedding-3-small": {"prompt": 0.02, "completion": 0.0},
}


def estimate_token_cost(
    model_name: str, prompt_tokens: int, completion_tokens: int = 0
) -> Dict[str, float]:
    """Calcula el costo proyectado en USD para una llamada a LLM."""
    pricing = MODEL_PRICING.get(model_name, MODEL_PRICING["gpt-4o-mini"])
    cost_prompt = (prompt_tokens / 1_000_000) * pricing["prompt"]
    cost_comp = (completion_tokens / 1_000_000) * pricing["completion"]
    total_cost = cost_prompt + cost_comp

    return {
        "prompt_tokens": prompt_tokens,
        "completion_tokens": completion_tokens,
        "total_tokens": prompt_tokens + completion_tokens,
        "estimated_cost_usd": round(total_cost, 6),
    }
