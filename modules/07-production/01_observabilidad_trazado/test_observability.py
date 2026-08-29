"""Suite de pruebas automatizadas para la instrumentación, observabilidad y guardrail de abstención."""

import json
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Cargar entorno
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[2] / "pre_entrega_06" / ".env")

from abstention_guardrail import evaluate_grounding_and_abstention
from graph import graph
from state import AgentState, AnalysisArtifact, ResearchArtifact
from tools.analysis_tools import calculate_cagr_and_growth
from tools.search_tools import query_chroma_vector_db
from tracer_setup import init_tracing


class TestObservabilitySuite:
    """Pruebas de la capa de trazabilidad, observabilidad y guardrails."""

    def test_tracer_initialization(self):
        res = init_tracing()
        assert res is True

    def test_chroma_vector_search(self):
        res_str = query_chroma_vector_db.invoke({"query": "mercado ia generativa", "k": 2})
        res = json.loads(res_str)
        assert res["status"] == "success"
        assert res["total_retrieved"] >= 1

    def test_grounding_guardrail_pass_and_abstain(self):
        # 1. Caso Grounded
        grounded_chunks = [{"content": "IA Generativa mercado USD 67B", "relevance_score": 0.38}]
        report_ok = evaluate_grounding_and_abstention("mercado ia", grounded_chunks)
        assert report_ok.is_grounded is True
        assert report_ok.status == "GROUNDED"

        # 2. Caso Abstención
        ungrounded_chunks = [{"content": "Texto no relacionado", "relevance_score": 0.08}]
        report_fail = evaluate_grounding_and_abstention("fusion nuclear 2045", ungrounded_chunks)
        assert report_fail.is_grounded is False
        assert report_fail.status == "ABSTAINED"

    def test_end_to_end_grounded_flow(self):
        initial_state: AgentState = {
            "messages": [HumanMessage(content="Analiza el mercado de IA Generativa y calcula su CAGR.")],
            "next_agent": "supervisor",
            "research_data": None,
            "analysis_data": None,
            "final_summary": None,
            "iteration_count": 0,
            "is_grounded": True,
            "abstention_report": None,
            "error": None
        }
        final_state = graph.invoke(initial_state)
        assert final_state["is_grounded"] is True
        assert final_state["research_data"] is not None
        assert final_state["analysis_data"] is not None

    def test_end_to_end_abstention_flow(self):
        initial_state: AgentState = {
            "messages": [HumanMessage(content="Telemetría de reactores de fusión nuclear cuántica del año 2045.")],
            "next_agent": "supervisor",
            "research_data": None,
            "analysis_data": None,
            "final_summary": None,
            "iteration_count": 0,
            "is_grounded": True,
            "abstention_report": None,
            "error": None
        }
        final_state = graph.invoke(initial_state)
        assert final_state["is_grounded"] is False
        assert "ABSTENCIÓN" in final_state["final_summary"]


if __name__ == "__main__":
    print("=" * 75)
    print("🧪 EJECUTANDO SUITE DE PRUEBAS DE OBSERVABILIDAD Y GUARDRAILS")
    print("=" * 75)
    suite = TestObservabilitySuite()
    suite.test_tracer_initialization()
    print("✅ 1/5 Tracer Initialization: OK")
    suite.test_chroma_vector_search()
    print("✅ 2/5 ChromaDB Vector Search: OK")
    suite.test_grounding_guardrail_pass_and_abstain()
    print("✅ 3/5 Grounding Guardrail (Grounded & Abstention): OK")
    suite.test_end_to_end_grounded_flow()
    print("✅ 4/5 End-to-End Grounded Flow (Q1): OK")
    suite.test_end_to_end_abstention_flow()
    print("✅ 5/5 End-to-End Safe Abstention Flow (Q6): OK")
    print("=" * 75)
    print("🎉 TODAS LAS PRUEBAS DE OBSERVABILIDAD Y CONTROL PASARON AL 100%")
    print("=" * 75)
