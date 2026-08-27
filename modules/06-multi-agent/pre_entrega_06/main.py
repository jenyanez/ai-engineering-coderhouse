"""Punto de entrada interactivo y CLI para ejecutar el Orquestador Multi-Agente."""

import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[1] / "pre_entrega_05" / ".env")

from graph import graph


def run_orchestrator(query: str):
    """Ejecuta el flujo multi-agente e imprime la traza de delegación paso a paso."""
    print("=" * 75)
    print("🤖 ORQUESTADOR MULTI-AGENTE JERÁRQUICO (LANGGRAPH)")
    print("=" * 75)
    print(f"📥 Consulta del Usuario: \"{query}\"\n")
    print("--- 🔄 TRAZA DE DELEGACIÓN PASO A PASO ---")

    initial_state = {
        "messages": [HumanMessage(content=query)],
        "next_agent": "supervisor",
        "research_data": None,
        "analysis_data": None,
        "final_summary": None,
        "iteration_count": 0,
        "error": None
    }

    step_count = 1
    for event in graph.stream(initial_state):
        for node_name, output in event.items():
            print(f"\n[Paso {step_count}] 🏷️ Nodo Activo: '{node_name}'")
            
            if "next_agent" in output:
                print(f"   👉 Decisión del Supervisor: next_agent -> '{output['next_agent']}'")
                print(f"   🔢 Iteración actual: {output.get('iteration_count', step_count)}")
                
            if "messages" in output:
                for msg in output["messages"]:
                    sender = getattr(msg, "name", "Sistema")
                    print(f"\n💬 [{sender}]:\n{msg.content}\n")
                    
            step_count += 1
            print("-" * 75)

    print("\n" + "=" * 75)
    print("✅ FLUJO COMPLETADO EXITOSAMENTE")
    print("=" * 75)


if __name__ == "__main__":
    default_query = (
        "Investiga las proyecciones de mercado y tasas de adopción de IA Generativa "
        "para el período 2024-2030 y calcula la tasa de crecimiento anual compuesta (CAGR)."
    )
    
    import sys
    user_input = sys.argv[1] if len(sys.argv) > 1 else default_query
    run_orchestrator(user_input)
