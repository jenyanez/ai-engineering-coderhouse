"""Pruebas unitarias de componentes, guardrails y RedisCheckpointer."""

import pytest
from app.core.checkpointer import RedisCheckpointer
from app.core.guardrails import generate_abstention_message, is_in_knowledge_domain
from app.core.state import QueryRequest, ResearchPayload
from app.observability.finops import estimate_token_cost
from app.tools.compute_tool import calculate_cagr


def test_guardrails_domain_check():
    """Valida detección correcta de dominio vs fuera de dominio."""
    assert is_in_knowledge_domain("¿Cuál es el CAGR de IA Generativa?") is True
    assert is_in_knowledge_domain("Receta para hornear pan de masa madre") is False


def test_abstention_message_structure():
    """Valida formato estructurado del mensaje de abstención activa."""
    msg = generate_abstention_message("pregunta no relacionada")
    assert "INFORMACIÓN NO DISPONIBLE" in msg
    assert "GUARDRAIL DE VERACIDAD" in msg


def test_cagr_calculation_tool():
    """Valida exactitud matemática de la herramienta de proyecciones."""
    res = calculate_cagr.invoke({"val_start": 67.0, "val_end": 1300.0, "years": 6})
    assert res["valid_analysis"] is True
    assert res["cagr_percentage"] > 60.0
    assert res["expansion_factor"] == 19.4


def test_finops_token_estimation():
    """Valida estimador de costos y conteo de tokens."""
    cost = estimate_token_cost("gpt-4o-mini", prompt_tokens=1000, completion_tokens=500)
    assert cost["total_tokens"] == 1500
    assert cost["estimated_cost_usd"] > 0.0


def test_redis_checkpointer_fallback_mechanism():
    """Valida que el RedisCheckpointer persista y recupere tuplas de checkpoint."""
    checkpointer = RedisCheckpointer(redis_client=None, prefix="test_cp:")
    config = {
        "configurable": {
            "thread_id": "thread_abc_123",
            "checkpoint_ns": "",
            "checkpoint_id": "cp_001",
        }
    }
    checkpoint = {
        "v": 1,
        "id": "cp_001",
        "ts": "2026-09-04T00:00:00Z",
        "channel_values": {"query": "test query"},
        "channel_versions": {"query": 1},
        "versions_seen": {},
    }
    saved_cfg = checkpointer.put(config, checkpoint, metadata={"source": "test"}, new_versions={"query": 1})
    assert saved_cfg["configurable"]["checkpoint_id"] == "cp_001"

    loaded = checkpointer.get_tuple(config)
    assert loaded is not None
    assert loaded.checkpoint["id"] == "cp_001"
