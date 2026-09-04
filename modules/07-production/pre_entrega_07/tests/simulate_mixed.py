"""Simulación de 3 pruebas automáticas y 3 pruebas con autorización HITL."""

import json
import time
import urllib.request

base_url = "http://localhost:8000"

test_cases = [
    # 3 AUTOMÁTICAS
    {"tipo": "⚡ AUTOMÁTICA (Sin HITL)", "user": "1. Analista de Operaciones", "query": "¿Qué métricas de latencia y precisión diferencian el chunking por tokens en RAG?", "require_hitl": False},
    {"tipo": "⚡ AUTOMÁTICA (Sin HITL)", "user": "2. Consultor de Estrategia", "query": "¿Cuál es la tasa de adopción de IA en empresas Fortune 500 y sectores líderes?", "require_hitl": False},
    {"tipo": "⚡ AUTOMÁTICA (Sin HITL)", "user": "3. Ingeniero de Datos", "query": "¿Cómo optimizan los embeddings de OpenAI la recuperación en bases de datos vectoriales?", "require_hitl": False},

    # 3 CON HITL
    {"tipo": "🛑 CRÍTICA (Requiere Autorización HITL)", "user": "4. Director de Finanzas", "query": "Informe crítico de inversión en infraestructura de agentes autónomos y presupuesto 2026", "require_hitl": True},
    {"tipo": "🛑 CRÍTICA (Requiere Autorización HITL)", "user": "5. Oficial de Riesgos", "query": "Evaluación de riesgos operativos, auditoría y mitigación de fallos en sistemas multi-agente", "require_hitl": True},
    {"tipo": "🛑 CRÍTICA (Requiere Autorización HITL)", "user": "6. VP de Arquitectura", "query": "Proyección financiera de costos y CAGR del mercado de IA Generativa al 2030", "require_hitl": True},
]

print("=" * 85)
print("🚀 EJECUTANDO SIMULACIÓN: 3 AUTOMÁTICAS + 3 CON AUTORIZACIÓN HITL")
print("=" * 85)

jobs = []
for tc in test_cases:
    payload = {"query": tc["query"], "priority": "high", "require_human_approval": tc["require_hitl"]}
    req = urllib.request.Request(f"{base_url}/tasks", data=json.dumps(payload).encode("utf-8"), headers={"Content-Type": "application/json"})
    t0 = time.time()
    with urllib.request.urlopen(req) as res:
        data = json.loads(res.read().decode("utf-8"))
        ms = (time.time() - t0) * 1000
        jobs.append({"meta": tc, "job_id": data["job_id"], "dispatch_ms": ms})
        print(f"[{tc['tipo']}]")
        print(f"  👤 Usuario: {tc['user']}")
        print(f"  ❓ Consulta: {tc['query']}")
        print(f"  ⚡ Job ID: {data['job_id']} | Despachado en {ms:.2f}ms\n")

print("-" * 85)
print("🔄 Monitoreando ejecución y resolviendo aprobaciones pendientes...\n")
time.sleep(0.4)

for j in jobs:
    job_id = j["job_id"]
    meta = j["meta"]

    # Consultar estado
    with urllib.request.urlopen(f"{base_url}/tasks/{job_id}") as res:
        status_data = json.loads(res.read().decode("utf-8"))

    if not meta["require_hitl"]:
        print(f"✅ [AUTOMÁTICA FINALIZADA] {meta['user']} -> Estado: {status_data['status']} (Sin pausa humana)")
    else:
        inter = status_data.get("intermediate_summary") or "Revisión requerida"
        print(f"🛑 [HITL PAUSADO] {meta['user']} -> Estado: {status_data['status']} | Resumen: {inter[:45]}...")
        # Enviar autorización
        app_payload = {"approved": True, "feedback": f"Autorizado por Comité Directivo para {meta['user']}"}
        req = urllib.request.Request(f"{base_url}/tasks/{job_id}/approve", data=json.dumps(app_payload).encode("utf-8"), headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req) as res:
            app_res = json.loads(res.read().decode("utf-8"))
            print(f"   ↳ 👤 [DECISIÓN HUMANA ENVIADA] -> {app_res['message']} (Estado final: {app_res['status']})\n")

print("=" * 85)
print("🎉 ¡Pruebas finalizadas con éxito! Abre http://localhost:8000/dashboard")
print("=" * 85)
