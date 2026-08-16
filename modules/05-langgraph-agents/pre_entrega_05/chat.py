"""
Pre-entrega 5: Agente de Razonamiento Cíclico con Memoria Persistente
Archivo: chat.py — Interfaz de Terminal Interactiva

Permite a un evaluador chatear libremente con el agente
en vivo desde la terminal, demostrando la persistencia
y el razonamiento autónomo fuera del script de demostración.
"""

import asyncio
from graph import create_agent_graph
from checkpointer import get_checkpointer
from langchain_core.messages import HumanMessage


async def chat():
    print("=" * 65)
    print("🤖 CHAT INTERACTIVO — PRE-ENTREGA 5")
    print("Escribe 'salir' o 'exit' para terminar la sesión.")
    print("El agente recordará el contexto de esta conversación.")
    print("=" * 65)

    thread_id = "sesion_interactiva_1"
    
    async with get_checkpointer() as checkpointer:
        app = create_agent_graph(checkpointer)
        config = {"configurable": {"thread_id": thread_id}, "recursion_limit": 10}

        while True:
            try:
                user_input = input("\n👤 Tú: ")
                if user_input.lower() in ["salir", "exit", "quit"]:
                    print("\n¡Hasta luego!")
                    break
                if not user_input.strip():
                    continue

                print("🤖 Agente: Pensando...", end="\r")
                
                # Ejecutar el grafo
                result = await app.ainvoke(
                    {"messages": [HumanMessage(content=user_input)]},
                    config=config
                )
                
                # Mostrar la respuesta final
                last_msg = result["messages"][-1]
                print(f"🤖 Agente: {last_msg.content}")

            except EOFError:
                print("\n¡Hasta luego!")
                break
            except Exception as e:
                print(f"\n⚠️ Ocurrió un error: {str(e)}")


if __name__ == "__main__":
    try:
        asyncio.run(chat())
    except KeyboardInterrupt:
        print("\nSesión terminada por el usuario.")
