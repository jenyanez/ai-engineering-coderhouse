"""Suite de pruebas unitarias y de integración para el Orquestador Multi-Agente con ChromaDB."""

import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Cargar entorno
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[1] / "pre_entrega_05" / ".env")

from agents.supervisor_agent import supervisor_node
from graph import graph
from state import AgentState, AnalysisArtifact, ResearchArtifact, RouterDecision
from tools.analysis_tools import calculate_cagr_and_growth, compute_statistical_metrics
from tools.search_tools import query_chroma_vector_db, query_tech_knowledge_base, search_market_trends


class TestTools:
    """Pruebas unitarias de las herramientas funcionales y Vector DB."""
    
    def test_query_chroma_vector_db(self):
        res_str = query_chroma_vector_db.invoke({"query": "mercado ia generativa 2024 2030", "k": 3})
        res = json.loads(res_str)
        assert res["status"] == "success"
        assert res["total_retrieved"] >= 1
        all_text = " ".join(c["content"] for c in res["chunks"])
        assert "67.0" in all_text or "1300.0" in all_text or "Generativa" in all_text

    def test_search_market_trends(self):
        res_str = search_market_trends.invoke({"query": "ia generativa"})
        res = json.loads(res_str)
        assert res["status"] == "success"
        assert res["total_retrieved"] >= 1

    def test_query_tech_knowledge_base(self):
        res_str = query_tech_knowledge_base.invoke({"topic": "sistemas multi-agente"})
        res = json.loads(res_str)
        assert res["status"] == "success"

    def test_calculate_cagr_and_growth(self):
        res_str = calculate_cagr_and_growth.invoke({"start_value": 100.0, "end_value": 200.0, "periods": 2})
        res = json.loads(res_str)
        assert res["cagr_percentage"] == 41.42
        assert res["total_growth_percentage"] == 100.0
        assert res["multiplier"] == 2.0

    def test_compute_statistical_metrics(self):
        res_str = compute_statistical_metrics.invoke({"values_json": "[10, 20, 30]"})
        res = json.loads(res_str)
        assert res["mean"] == 20.0
        assert res["median"] == 20.0


class TestStateSchemas:
    """Pruebas de validación de esquemas Pydantic V2."""
    
    def test_research_artifact_valid(self):
        artifact = ResearchArtifact(
            topic="IA Generativa",
            summary="Resumen de prueba con longitud suficiente",
            key_metrics=["Crecimiento 20%"],
            sources=["ia_generativa_market_2025.md"],
            confidence_score=0.95
        )
        assert artifact.topic == "IA Generativa"
        assert artifact.confidence_score == 0.95

    def test_analysis_artifact_valid(self):
        artifact = AnalysisArtifact(
            analysis_type="CAGR",
            calculated_metrics="CAGR: 63.92%",
            interpretation="Interpretación técnica detallada y extensa",
            recommendations=["Invertir en I+D"]
        )
        assert artifact.analysis_type == "CAGR"

    def test_router_decision_valid(self):
        decision = RouterDecision(
            next_agent="Investigador",
            reasoning="Se requieren datos iniciales",
            is_sufficient=False
        )
        assert decision.next_agent == "Investigador"


class TestSupervisorAndGraph:
    """Pruebas de integración del flujo de orquestación y guardrails."""
    
    def test_anti_loop_guardrail(self):
        state: AgentState = {
            "messages": [HumanMessage(content="Consulta de prueba")],
            "next_agent": "supervisor",
            "research_data": None,
            "analysis_data": None,
            "final_summary": None,
            "iteration_count": 6,
            "error": None
        }
        res = supervisor_node(state)
        assert res["next_agent"] == "FINALIZAR"
        assert res["iteration_count"] == 7

    def test_end_to_end_graph_execution(self):
        initial_state: AgentState = {
            "messages": [HumanMessage(content="Investiga el mercado de sistemas multi-agente en ChromaDB y calcula su crecimiento.")],
            "next_agent": "supervisor",
            "research_data": None,
            "analysis_data": None,
            "final_summary": None,
            "iteration_count": 0,
            "error": None
        }
        final_state = graph.invoke(initial_state)
        assert final_state["research_data"] is not None
        assert final_state["analysis_data"] is not None
        assert final_state["final_summary"] is not None
        assert len(final_state["messages"]) >= 4


if __name__ == "__main__":
    print("=" * 70)
    print("🧪 EJECUTANDO SUITE DE PRUEBAS DEL ORQUESTADOR CON CHROMADB")
    print("=" * 70)
    t = TestTools()
    t.test_query_chroma_vector_db()
    t.test_search_market_trends()
    t.test_query_tech_knowledge_base()
    t.test_calculate_cagr_and_growth()
    t.test_compute_statistical_metrics()
    print("✅ TestTools: 5/5 pasados con éxito")
    
    s = TestStateSchemas()
    s.test_research_artifact_valid()
    s.test_analysis_artifact_valid()
    s.test_router_decision_valid()
    print("✅ TestStateSchemas: 3/3 pasados con éxito")
    
    g = TestSupervisorAndGraph()
    g.test_anti_loop_guardrail()
    g.test_end_to_end_graph_execution()
    print("✅ TestSupervisorAndGraph: 2/2 pasados con éxito")
    print("\n" + "=" * 70)
    print("🎉 TODAS LAS PRUEBAS UNITARIAS Y DE INTEGRACIÓN PASARON AL 100% (10/10)")
    print("=" * 70)
