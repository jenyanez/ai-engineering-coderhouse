"""
Pre-entrega 5: Agente de Razonamiento Cíclico con Memoria Persistente
Archivo: test_agent.py — Pruebas Automatizadas

Verifica la compilación del grafo, el funcionamiento del checkpointer
y la respuesta básica del agente ante un prompt directo.
"""

import pytest
import aiosqlite
from langchain_core.messages import HumanMessage
from graph import create_agent_graph
from checkpointer import get_checkpointer
from tools import buscar_pedidos


@pytest.mark.asyncio
async def test_tool_buscar_pedidos_existente():
    """Verifica que la herramienta responda correctamente para un cliente válido."""
    resultado = buscar_pedidos.invoke({"cliente_id": 102})
    assert "Cliente 102" in resultado
    assert "14,500" in resultado


@pytest.mark.asyncio
async def test_tool_buscar_pedidos_inexistente():
    """Verifica que la herramienta controle errores de clientes no válidos."""
    resultado = buscar_pedidos.invoke({"cliente_id": 999})
    assert "Error: No se encontró" in resultado
    assert "999" in resultado


@pytest.mark.asyncio
async def test_agent_graph_compilation():
    """Verifica que el grafo compile correctamente con el AsyncSqliteSaver."""
    # Usar una base de datos en memoria para los tests
    async with get_checkpointer(":memory:") as checkpointer:
        app = create_agent_graph(checkpointer)
        assert app is not None
        assert app.name == "LangGraph"


@pytest.mark.asyncio
async def test_agent_memory_persistence():
    """Simula una conversación básica para verificar que no crashea con la persistencia."""
    async with get_checkpointer(":memory:") as checkpointer:
        app = create_agent_graph(checkpointer)
        config = {"configurable": {"thread_id": "test_thread"}, "recursion_limit": 5}
        
        # Test: saludo sin invocar herramientas
        result = await app.ainvoke(
            {"messages": [HumanMessage(content="Hola, ¿qué puedes hacer?")]},
            config=config
        )
        
        assert len(result["messages"]) > 1
        last_msg = result["messages"][-1]
        assert len(last_msg.content) > 0
