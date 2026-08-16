"""
Pre-entrega 5: Agente de Razonamiento Cíclico con Memoria Persistente
Archivo: main.py — Orquestador Principal

Ejecuta una demostración del agente ReAct en 3 pasos con el mismo thread_id,
demostrando razonamiento multi-paso (≥2 tool_calls) y persistencia de contexto.
Exporta la traza completa de ejecución a traza_ejecucion.json.
"""

import asyncio
import json
from datetime import datetime, timezone
from langchain_core.messages import HumanMessage
from graph import create_agent_graph
from checkpointer import get_checkpointer


# Límite de recursión para evitar bucles infinitos y costos inesperados
RECURSION_LIMIT: int = 10
THREAD_ID: str = "sesion_cliente_demo"


def _serialize_messages(messages: list) -> list[dict]:
    """Convierte los mensajes de LangChain a diccionarios serializables."""
    serialized = []
    for msg in messages:
        entry: dict = {
            "type": msg.type,
            "content": msg.content,
        }
        # Incluir tool_calls si existen (mensajes del tipo AIMessage)
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            entry["tool_calls"] = [
                {
                    "name": tc["name"],
                    "args": tc["args"],
                    "id": tc.get("id", ""),
                }
                for tc in msg.tool_calls
            ]
        # Incluir tool_call_id para ToolMessages
        if hasattr(msg, "tool_call_id") and msg.tool_call_id:
            entry["tool_call_id"] = msg.tool_call_id
        serialized.append(entry)
    return serialized


async def run_step(
    app,
    query: str,
    step_num: int,
    config: dict,
    trace_log: list,
) -> dict:
    """Ejecuta un paso de conversación, imprime el resultado y lo registra."""
    print(f"\n{'='*65}")
    print(f"📍 PASO {step_num}")
    print(f"{'='*65}")
    print(f"👤 Usuario: {query}")

    result = await app.ainvoke(
        {"messages": [HumanMessage(content=query)]},
        config=config,
    )

    last_msg = result["messages"][-1]
    print(f"🤖 Agente: {last_msg.content}")
    print(f"📊 Mensajes acumulados en sesión: {len(result['messages'])}")

    # Registrar en la traza
    trace_log.append({
        "paso": step_num,
        "usuario": query,
        "respuesta_agente": last_msg.content,
        "total_mensajes": len(result["messages"]),
        "mensajes_detalle": _serialize_messages(result["messages"]),
    })

    return result


async def main() -> None:
    print("=" * 65)
    print("🤖 PRE-ENTREGA 5: AGENTE REACT CON SQLITESAVER")
    print("=" * 65)
    print(f"Thread ID: {THREAD_ID}")
    print(f"Recursion Limit: {RECURSION_LIMIT}")

    # Abrir el checkpointer SqliteSaver dentro del context manager
    async with get_checkpointer() as checkpointer:
        # Compilar el agente con SqliteSaver
        app = create_agent_graph(checkpointer)

        # Configuración de sesión y límite de recursión
        config: dict = {
            "configurable": {"thread_id": THREAD_ID},
            "recursion_limit": RECURSION_LIMIT,
        }

        trace_log: list = []

        # ──────────────────────────────────────────────
        # Paso 1: Consulta de pedidos (1er tool_call)
        # ──────────────────────────────────────────────
        await run_step(
            app,
            query="¿Cuántos pedidos tuvo el cliente 102 y cuál fue el total?",
            step_num=1,
            config=config,
            trace_log=trace_log,
        )

        # ──────────────────────────────────────────────
        # Paso 2: Consulta de producto (2do tool_call, multi-paso)
        # El agente recuerda el contexto y deduce el producto_id
        # ──────────────────────────────────────────────
        await run_step(
            app,
            query="¿Y cuál fue el último producto que compró? Dame nombre y precio.",
            step_num=2,
            config=config,
            trace_log=trace_log,
        )

        # ──────────────────────────────────────────────
        # Paso 3: Consulta de envío (3er tool_call, memoria persistente)
        # El agente recuerda pedido_id sin que el usuario lo repita
        # ──────────────────────────────────────────────
        await run_step(
            app,
            query="¿En qué estado está el envío de ese pedido?",
            step_num=3,
            config=config,
            trace_log=trace_log,
        )

        # ──────────────────────────────────────────────
        # Paso 4: Auto-Recuperación y Manejo de Errores
        # Demuestra cómo el agente procesa un error de la herramienta y responde útilmente
        # ──────────────────────────────────────────────
        await run_step(
            app,
            query="Perfecto. Ahora dime, ¿cuántos pedidos tiene el cliente 999?",
            step_num=4,
            config=config,
            trace_log=trace_log,
        )

        # ──────────────────────────────────────────────
        # Exportar traza de ejecución a JSON
        # ──────────────────────────────────────────────
        trace_output = {
            "metadata": {
                "proyecto": "Pre-entrega 5: Agente ReAct con Memoria Persistente",
                "thread_id": THREAD_ID,
                "recursion_limit": RECURSION_LIMIT,
                "timestamp": datetime.now(timezone.utc).isoformat(),
            },
            "traza": trace_log,
        }

        output_path = "traza_ejecucion.json"
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(trace_output, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*65}")
        print(f"✅ EJECUCIÓN COMPLETADA")
        print(f"📄 Traza exportada a: {output_path}")
        print(f"{'='*65}\n")


if __name__ == "__main__":
    asyncio.run(main())

