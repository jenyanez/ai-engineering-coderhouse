"""Generador de tráfico y benchmark de observabilidad con guardrail de abstención para Arize Phoenix."""

import time
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Cargar entorno
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / "pre_entrega_06" / ".env")

from graph import graph
from tracer_setup import init_tracing

# Inicializar exportadores de telemetría
init_tracing()

BENCHMARK_QUERIES = [
    {
        "id": "Q1",
        "category": "RAG + CAGR",
        "description": "Mercado y CAGR de IA Generativa (2024-2030)",
        "query": "Investiga las proyecciones de mercado y tasas de adopción de IA Generativa para el período 2024-2030 y calcula el CAGR estimado."
    },
    {
        "id": "Q2",
        "category": "RAG + Multiplicador",
        "description": "Sistemas Multi-Agente: Tamaño y tasa de crecimiento",
        "query": "Analiza el mercado de Sistemas Multi-Agente entre 2024 y 2030, y calcula el multiplicador y tasa de crecimiento total."
    },
    {
        "id": "Q3",
        "category": "RAG + Riesgos Técnicos",
        "description": "RAG Avanzado: Métricas y riesgos en retrieval",
        "query": "Recopila las métricas de mercado de RAG Avanzado y bases vectoriales, e interpreta los principales riesgos técnicos."
    },
    {
        "id": "Q4",
        "category": "Arquitectura y Patrones",
        "description": "Patrón Supervisor: Drivers y prevención de bucles",
        "query": "Investiga los factores impulsores del Patrón Supervisor y cómo previene condiciones de carrera y bucles infinitos."
    },
    {
        "id": "Q5",
        "category": "Comparativa Multi-Dominio",
        "description": "Análisis comparativo de crecimiento entre tecnologías",
        "query": "Realiza un análisis comparativo de inversión y crecimiento proyectado entre IA Generativa y Sistemas Multi-Agente."
    },
    {
        "id": "Q6-FALLO",
        "category": "Fallo Inducido (Out-of-Domain)",
        "description": "Consulta fuera de dominio con guardrail de abstención",
        "query": "Investiga los datos de telemetría de reactores de fusión nuclear cuántica del año 2045 y calcula su eficiencia energética."
    }
]


def run_traffic_generation():
    """Ejecuta el lote de consultas y registra los tiempos de respuesta y spans."""
    print("=" * 80)
    print("🔥 GENERADOR DE TRÁFICO Y BENCHMARK DE OBSERVABILIDAD CON GUARDRAIL")
    print("=" * 80)
    print(f"📊 Dashboard local disponible en: http://localhost:6006")
    print(f"🎯 Total de consultas a procesar: {len(BENCHMARK_QUERIES)}\n")

    results = []

    for item in BENCHMARK_QUERIES:
        q_id = item["id"]
        category = item["category"]
        query_text = item["query"]
        
        print(f"\n[{q_id}] 🚀 Ejecutando: '{item['description']}' ({category})")
        print(f"    📥 Query: \"{query_text}\"")

        initial_state = {
            "messages": [HumanMessage(content=query_text)],
            "next_agent": "supervisor",
            "research_data": None,
            "analysis_data": None,
            "final_summary": None,
            "iteration_count": 0,
            "is_grounded": True,
            "abstention_report": None,
            "error": None
        }

        t_start = time.perf_counter()
        try:
            final_state = graph.invoke(initial_state)
            elapsed = time.perf_counter() - t_start
            
            grounded_status = "✅ GROUNDED" if final_state.get("is_grounded") else "🛑 ABSTENCIÓN"
            action_status = "SÍNTESIS" if final_state.get("is_grounded") else "SAFE_REFUSAL"
            
            print(f"    ⏱️ Latencia Total: {elapsed:.3f} s")
            print(f"    🛡️ Grounding Guardrail: {grounded_status} | Acción: {action_status}")
            
            results.append({
                "id": q_id,
                "category": category,
                "latency_s": round(elapsed, 3),
                "grounding": grounded_status,
                "status": "COMPLETADO"
            })
        except Exception as exc:
            elapsed = time.perf_counter() - t_start
            print(f"    ❌ Error capturado en traza: {exc}")
            results.append({
                "id": q_id,
                "category": category,
                "latency_s": round(elapsed, 3),
                "grounding": "ERROR",
                "status": f"ERROR: {exc}"
            })
            
        time.sleep(1)  # Pausa para separación de spans

    print("\n" + "=" * 85)
    print("📋 RESUMEN FINAL DEL BENCHMARK DE TRÁFICO Y GUARDRAILS")
    print("=" * 85)
    print(f"{'ID':<10} | {'Categoría':<26} | {'Latencia (s)':<13} | {'Grounding':<16} | {'Estado'}")
    print("-" * 85)
    for r in results:
        print(f"{r['id']:<10} | {r['category']:<26} | {r['latency_s']:<13.3f} | {r['grounding']:<16} | {r['status']}")
    
    latencies = [r["latency_s"] for r in results if "ERROR" not in r["status"]]
    if latencies:
        avg_lat = sum(latencies) / len(latencies)
        max_lat = max(latencies)
        min_lat = min(latencies)
        print("-" * 85)
        print(f"📈 Métricas de Latencia: Promedio = {avg_lat:.3f} s | Min = {min_lat:.3f} s | Max = {max_lat:.3f} s")
    print("=" * 85)
    print("👉 Abre http://localhost:6006 en tu navegador para inspeccionar las trazas detalladas.")


if __name__ == "__main__":
    run_traffic_generation()
