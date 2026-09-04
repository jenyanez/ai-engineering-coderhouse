"""Pruebas de integración para endpoints FastAPI y ciclo de vida de jobs."""

import pytest
from httpx import ASGITransport, AsyncClient
from app.main import app


@pytest.mark.asyncio
async def test_health_check_endpoint():
    """Valida endpoint /health de la API."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


@pytest.mark.asyncio
async def test_submit_query_and_polling():
    """Valida encolamiento asíncrono y consulta de estado."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # 1. Encolar consulta
        res_post = await client.post(
            "/api/v1/query",
            json={"query": "¿Cuál es la proyección del mercado de IA Generativa en 2030?"},
        )
        assert res_post.status_code == 202
        post_data = res_post.json()
        assert "job_id" in post_data
        assert post_data["status"] == "pending"

        # 2. Consultar estado (polling)
        job_id = post_data["job_id"]
        res_get = await client.get(f"/api/v1/jobs/{job_id}")
        assert res_get.status_code == 200
        get_data = res_get.json()
        assert get_data["job_id"] == job_id
        assert get_data["query"] == "¿Cuál es la proyección del mercado de IA Generativa en 2030?"


@pytest.mark.asyncio
async def test_hitl_approval_endpoint():
    """Valida resolución de aprobación humana en tareas."""
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        # Encolar una tarea primero
        res = await client.post("/api/v1/query", json={"query": "Análisis crítico de inversión"})
        job_id = res.json()["job_id"]

        # Simular que el estado es waiting_human_approval
        from app.api.store import task_store

        task = await task_store.get_task(job_id)
        task["status"] = "waiting_human_approval"
        await task_store.set_task(job_id, task)

        # Resolver HITL vía endpoint
        approve_res = await client.post(
            f"/api/v1/jobs/{job_id}/approve",
            json={"approved": True, "feedback": "Autorizado por auditor"},
        )
        assert approve_res.status_code == 200
        assert approve_res.json()["hitl_approved"] is True
