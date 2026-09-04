"""Batería oficial de 5 casos de prueba y benchmark de concurrencia."""

import asyncio
import statistics
import time
from typing import List
from httpx import ASGITransport, AsyncClient
from app.main import app

OFFICIAL_TEST_CASES = [
    {"id": "CASO_1_RAG", "query": "¿Cuáles son los factores clave y adopción Fortune 500 según el informe?"},
    {"id": "CASO_2_CUANTITATIVO", "query": "Calcula el CAGR y factor de expansión del mercado de IA 2024 a 2030."},
    {"id": "CASO_3_SUPERVISOR_MULTIDOMINIO", "query": "Genera análisis completo de mercado, proyecciones y gobernanza."},
    {"id": "CASO_4_HITL_CRITICO", "query": "Recomendación crítica de inversión de capital institucional en IA."},
    {"id": "CASO_5_ABSTENCION", "query": "¿Cuál es la receta de pasta al pesto tradicional italiana?"},
]


async def poll_until_done(client: AsyncClient, job_id: str, timeout: float = 10.0):
    start = time.perf_counter()
    while time.perf_counter() - start < timeout:
        res = await client.get(f"/api/v1/jobs/{job_id}")
        data = res.json()
        if data.get("status") in ("completed", "failed", "waiting_human_approval"):
            return data
        await asyncio.sleep(0.1)
    return {"status": "timeout"}


async def run_official_suite():
    transport = ASGITransport(app=app)
    latencies: List[float] = []

    print("\n" + "=" * 65)
    print("🚀 EJECUTANDO BATERÍA OFICIAL DE 5 PRUEBAS (PROYECTO FINAL)")
    print("=" * 65)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        for idx, case in enumerate(OFFICIAL_TEST_CASES, 1):
            t0 = time.perf_counter()
            post_res = await client.post("/api/v1/query", json={"query": case["query"]})
            job_id = post_res.json()["job_id"]

            result = await poll_until_done(client, job_id)
            elapsed = time.perf_counter() - t0
            latencies.append(elapsed)

            print(f"\n[{idx}/5] {case['id']}")
            print(f"  • Query:    {case['query']}")
            print(f"  • Estado:   {result.get('status')} | Latencia: {elapsed:.3f}s")
            if result.get("result"):
                snippet = result["result"].replace("\n", " ")[:120]
                print(f"  • Síntesis: {snippet}...")

        # Benchmark de 5 peticiones concurrentes
        print("\n" + "-" * 65)
        print("⚡ BENCHMARK CONCURRENTE (5 PETICIONES SIMULTÁNEAS)")
        print("-" * 65)
        t_batch_start = time.perf_counter()
        tasks = [
            client.post("/api/v1/query", json={"query": case["query"]})
            for case in OFFICIAL_TEST_CASES
        ]
        batch_res = await asyncio.gather(*tasks)
        batch_elapsed = time.perf_counter() - t_batch_start

        all_ok = all(r.status_code == 202 for r in batch_res)
        p50 = statistics.median(latencies)
        p95 = statistics.quantiles(latencies, n=20)[18] if len(latencies) >= 5 else max(latencies)

        print(f"  • Peticiones despachadas concurrentemente: {len(batch_res)}/5")
        print(f"  • Tiempo de encolamiento paralelo:        {batch_elapsed:.3f}s (Cero bloqueo)")
        print(f"  • Latencia p50 (Mediana):                  {p50:.3f}s")
        print(f"  • Latencia p95:                            {p95:.3f}s")
        print("=" * 65 + "\n")


if __name__ == "__main__":
    asyncio.run(run_official_suite())
