import asyncio
import os
import time
from pathlib import Path
from typing import List, Optional, TypedDict
from dotenv import load_dotenv
from langgraph.graph import END, StateGraph
from pydantic import BaseModel, Field, ValidationError

load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[3] / "pre_entrega_05" / ".env")


# =====================================================================
# 1. Modelos de Validación con Pydantic
# =====================================================================
class ResearchArtifact(BaseModel):
    topic: str = Field(..., min_length=3, description="Tema investigado")
    summary: str = Field(..., min_length=10, description="Síntesis de los hallazgos")
    key_findings: List[str] = Field(..., min_length=1, description="Puntos clave")
    sources: List[str] = Field(default_factory=list, description="Fuentes consultadas")
    confidence_score: float = Field(..., ge=0.0, le=1.0, description="Score entre 0 y 1")


class ReviewArtifact(BaseModel):
    approved: bool = Field(..., description="Aprobación técnica")
    quality_score: float = Field(..., ge=0.0, le=1.0, description="Score de calidad entre 0 y 1")
    feedback: str = Field(..., min_length=5, description="Comentarios de revisión")
    recommendations: List[str] = Field(default_factory=list, description="Recomendaciones")


# =====================================================================
# 2. Estado Global Compartido (AgentState)
# =====================================================================
class AgentState(TypedDict):
    topic: str
    researcher_output: Optional[dict]
    reviewer_output: Optional[dict]
    error: Optional[str]


# =====================================================================
# Sub-procesos Asíncronos Concurrentes
# =====================================================================
async def fetch_academic_papers(topic: str) -> list[str]:
    """Simula consulta concurrente a repositorios académicos."""
    await asyncio.sleep(0.3)
    return [f"ArXiv:2408.{topic.replace(' ', '')}", "IEEE Multi-Agent Systems 2026"]


async def fetch_industry_benchmarks(topic: str) -> list[str]:
    """Simula consulta concurrente a benchmarks de la industria."""
    await asyncio.sleep(0.3)
    return ["LangGraph Benchmark Report", "Production Multi-Agent Survey"]


async def verify_policy_compliance(summary: str) -> bool:
    """Simula auditoría de compliance concurrente."""
    await asyncio.sleep(0.2)
    return len(summary) >= 10


async def evaluate_technical_depth(confidence: float) -> float:
    """Simula cálculo de profundidad técnica concurrente."""
    await asyncio.sleep(0.2)
    return min(1.0, confidence * 1.02)


# =====================================================================
# 3. Nodos Asíncronos con Concurrencia Real (asyncio.gather)
# =====================================================================
async def researcher_node(state: AgentState) -> dict:
    """Nodo Investigador: Ejecuta tareas de extracción en paralelo con asyncio.gather."""
    topic = state.get("topic", "Sistemas Multi-Agente")
    try:
        # CONCURRENCIA REAL: Ejecución en paralelo de fuentes independientes
        academic, benchmarks = await asyncio.gather(
            fetch_academic_papers(topic),
            fetch_industry_benchmarks(topic)
        )
        
        artifact = ResearchArtifact(
            topic=topic,
            summary=f"Investigación exhaustiva sobre {topic} integrando fuentes académicas e industriales.",
            key_findings=[
                "La concurrencia con asyncio.gather reduce el tiempo total de I/O a la duración de la tarea más lenta.",
                "El retorno de diccionarios inmutables previene colisiones en el estado compartido.",
                "Pydantic garantiza contratos de datos estructurados entre agentes."
            ],
            sources=academic + benchmarks,
            confidence_score=0.95
        )
        return {"researcher_output": artifact.model_dump(), "error": None}
    except (ValidationError, Exception) as exc:
        return {"error": f"Error en researcher_node: {str(exc)}", "researcher_output": None}


async def reviewer_node(state: AgentState) -> dict:
    """Nodo Revisor: Ejecuta verificaciones de calidad y compliance en paralelo."""
    if state.get("error"):
        return {"reviewer_output": None}
    research_data = state.get("researcher_output")
    if not research_data:
        return {"error": "Error: researcher_output ausente en el estado", "reviewer_output": None}
    try:
        research = ResearchArtifact(**research_data)
        
        # CONCURRENCIA REAL: Verificación de compliance y calidad en paralelo
        is_compliant, quality = await asyncio.gather(
            verify_policy_compliance(research.summary),
            evaluate_technical_depth(research.confidence_score)
        )
        
        review = ReviewArtifact(
            approved=is_compliant and quality >= 0.8,
            quality_score=round(quality, 2),
            feedback=f"Investigación sobre '{research.topic}' validada concurrentemente con {len(research.sources)} fuentes.",
            recommendations=["Preparar integración con almacenamiento persistente."]
        )
        return {"reviewer_output": review.model_dump(), "error": None}
    except (ValidationError, Exception) as exc:
        return {"error": f"Error en reviewer_node: {str(exc)}", "reviewer_output": None}


# =====================================================================
# 4. Configuración del Grafo
# =====================================================================
workflow = StateGraph(AgentState)
workflow.add_node("investigador", researcher_node)
workflow.add_node("revisor", reviewer_node)
workflow.set_entry_point("investigador")
workflow.add_edge("investigador", "revisor")
workflow.add_edge("revisor", END)
app = workflow.compile()


# =====================================================================
# 5. Ejecución Asíncrona y Medición de Tiempo
# =====================================================================
async def run_example():
    initial_state = {"topic": "Sistemas Multi-Agente", "researcher_output": None, "reviewer_output": None, "error": None}
    print("=" * 70)
    print("🚀 EJECUTANDO GRAFO ASÍNCRONO CON CONCURRENCIA REAL (asyncio.gather)")
    print("=" * 70)
    
    t0 = time.perf_counter()
    async for event in app.astream(initial_state):
        for node, output in event.items():
            print(f"\n🏷️ [Nodo: {node}]")
            if output.get("error"):
                print(f"   ⚠️ Error: {output['error']}")
            elif output.get("researcher_output"):
                r = output["researcher_output"]
                print(f"   📝 Resumen: {r['summary']}")
                print(f"   📚 Fuentes obtenidas en paralelo: {r['sources']}")
                print(f"   🎯 Confianza: {r['confidence_score'] * 100:.1f}%")
            elif output.get("reviewer_output"):
                rev = output["reviewer_output"]
                print(f"   🔍 Estado: {'✅ APROBADO' if rev['approved'] else '❌ RECHAZADO'}")
                print(f"   ⭐ Calidad: {rev['quality_score'] * 100:.1f}% | Feedback: {rev['feedback']}")
                
    elapsed = time.perf_counter() - t0
    print("\n" + "=" * 70)
    print(f"⏱️ Tiempo total de ejecución (con tareas paralelas): {elapsed:.3f} segundos")
    print("✅ PIPELINE ASÍNCRONO COMPLETADO CON ÉXITO")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(run_example())
