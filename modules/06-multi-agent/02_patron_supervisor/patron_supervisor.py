import os
from pathlib import Path
from typing import Annotated, Literal, TypedDict
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI
from langgraph.graph import END, StateGraph
from langgraph.graph.message import add_messages
from pydantic import BaseModel, Field

# Carga segura de variables de entorno (sin credenciales hardcodeadas)
load_dotenv(Path(__file__).resolve().parent / ".env")
load_dotenv(Path(__file__).resolve().parents[3] / "pre_entrega_05" / ".env")


# =====================================================================
# 1. Definición del Estado Global del Agente (AgentState)
# =====================================================================
class AgentState(TypedDict):
    """Estado global compartido con historial de mensajes y variable de ruteo."""
    messages: Annotated[list[BaseMessage], add_messages]
    next: Literal["Analista", "Escritor", "FINALIZAR"]


class RouterDecision(BaseModel):
    """Esquema de salida estructurada para la decisión del Supervisor."""
    next: Literal["Analista", "Escritor", "FINALIZAR"] = Field(
        description="Especialista al que se debe delegar o 'FINALIZAR' si la tarea está lista."
    )


# =====================================================================
# 2. Implementación del Nodo Supervisor
# =====================================================================
def supervisor_node(state: AgentState) -> dict:
    """Nodo Supervisor: Emplea el LLM para evaluar la conversación y enrutar."""
    llm = ChatOpenAI(
        model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
        temperature=0
    )
    
    system_prompt = (
        "Eres un supervisor encargado de gestionar una conversación entre los especialistas: "
        "['Analista', 'Escritor'].\n"
        "Reglas de delegación:\n"
        "1. Si el usuario solicita un análisis y aún no hay datos del 'Analista', delega a 'Analista'.\n"
        "2. Si el 'Analista' ya aportó datos procesados pero el 'Escritor' no ha redactado el informe, delega a 'Escritor'.\n"
        "3. Si el 'Escritor' ya generó el informe o la tarea está cumplida, responde 'FINALIZAR'.\n"
        "Dada la conversación, decide qué especialista debe actuar a continuación o si se debe FINALIZAR."
    )
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", system_prompt),
        MessagesPlaceholder(variable_name="messages"),
        ("system", "¿Quién debería actuar a continuación? Selecciona exactamente uno de: ['Analista', 'Escritor', 'FINALIZAR'].")
    ])
    
    chain = prompt | llm.with_structured_output(RouterDecision)
    decision = chain.invoke({"messages": state["messages"]})
    return {"next": decision.next}


# =====================================================================
# Nodos Especialistas (Workers)
# =====================================================================
def analyst_node(state: AgentState):
    return {"messages": [HumanMessage(content="Datos procesados: +20% incremento.", name="Analista")]}


def writer_node(state: AgentState):
    return {"messages": [HumanMessage(content="El informe está listo: Crecimiento positivo.", name="Escritor")]}


# =====================================================================
# 3. Configuración del Grafo (StateGraph y Aristas Condicionales)
# =====================================================================
builder = StateGraph(AgentState)

# Registrar nodos
builder.add_node("supervisor", supervisor_node)
builder.add_node("Analista", analyst_node)
builder.add_node("Escritor", writer_node)

# Establecer punto de entrada
builder.set_entry_point("supervisor")

# Aristas fijas: los especialistas retornan siempre el control al supervisor
builder.add_edge("Analista", "supervisor")
builder.add_edge("Escritor", "supervisor")

# Arista condicional: el supervisor delega dinámicamente según state['next']
builder.add_conditional_edges(
    "supervisor",
    lambda state: state["next"],
    {
        "Analista": "Analista",
        "Escritor": "Escritor",
        "FINALIZAR": END
    }
)

# Compilar grafo
graph = builder.compile()


# =====================================================================
# Bloque de Ejecución y Validación
# =====================================================================
if __name__ == "__main__":
    initial_input = {
        "messages": [
            HumanMessage(content="Por favor analiza los datos de ventas del último trimestre y genera un informe ejecutivo.")
        ]
    }
    
    print("=" * 70)
    print("🚀 INICIANDO EJECUCIÓN DEL PATRÓN SUPERVISOR (LANGGRAPH)")
    print("=" * 70)
    
    step_count = 1
    for step in graph.stream(initial_input):
        for node_name, output in step.items():
            print(f"\n[Paso {step_count}] 🏷️ Nodo ejecutado: '{node_name}'")
            if "next" in output:
                print(f"   👉 Decisión del Supervisor: next -> '{output['next']}'")
            if "messages" in output:
                for msg in output["messages"]:
                    sender = getattr(msg, "name", "Usuario")
                    print(f"   💬 [{sender}]: {msg.content}")
            step_count += 1
            
    print("\n" + "=" * 70)
    print("✅ EJECUCIÓN COMPLETADA EXITOSAMENTE (ESTADO: FINALIZAR)")
    print("=" * 70)
