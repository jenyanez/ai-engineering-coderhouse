# Ejercicio: El Patrón Supervisor — Delegación Dinámica

> **Programa:** AI Engineering — Coderhouse  
> **Módulo 6:** Sistemas Multi-Agente: Colaboración y Especialización  
> **Unidad 2:** Orquestación y Patrón Supervisor en LangGraph  

---

## 📌 Descripción del Ejercicio

Implementación del **Patrón Supervisor** en **LangGraph** para orquestar la colaboración entre agentes especialistas (*Analista* y *Escritor*). El Supervisor actúa como director de tráfico evaluando el historial conversacional y decidiendo dinámicamente el siguiente nodo a ejecutar mediante salidas estructuradas (*Structured Outputs*) de OpenAI.

---

## 🏗️ Topología del Grafo

```text
[▶ Inicio: Input del Usuario]
               │
               ▼
       ┌───────────────┐
       │ 👑 Supervisor │ ◄───────────────────────────┐
       └───────┬───────┘                             │
               │                                     │ (Retorna Estado)
        ¿state['next']?                              │
               ├─► [🎭 Analista] ────────────────────┤
               ├─► [✍️ Escritor] ────────────────────┘
               │
               └─► 'FINALIZAR' ──► [⏹️ END: Flujo Completado]
```

---

## 🧩 Componentes Implementados

1. **Estado Global (`AgentState`):**
   - `messages: Annotated[list[BaseMessage], add_messages]`: Historial de mensajes acumulado mediante el reducer `add_messages`.
   - `next: Literal["Analista", "Escritor", "FINALIZAR"]`: Variable de control de enrutamiento.

2. **Nodo Supervisor (`supervisor_node`):**
   - Emplea `ChatOpenAI` (`gpt-4o-mini`, `temperature=0`) con `with_structured_output(Router)` para forzar determinismo en la selección del especialista o la finalización.

3. **Nodos Especialistas:**
   - **`analyst_node`:** Procesa métricas cuantitativas y añade `HumanMessage(content="...", name="Analista")`.
   - **`writer_node`:** Redacta el informe ejecutivo basándose en el análisis y añade `HumanMessage(content="...", name="Escritor")`.

4. **Aristas y Ruteo Condicional:**
   - Aristas fijas de retorno: `Analista -> supervisor` y `Escritor -> supervisor`.
   - Arista condicional: `supervisor -> lambda state: state['next']` mapeando a `Analista`, `Escritor` o `END`.
   - Punto de entrada (`set_entry_point`): `'supervisor'`.

---

## 🚀 Guía de Ejecución

### 1. Requisitos
* Python 3.10+
* `langchain-openai`, `langgraph`, `pydantic`, `python-dotenv`

### 2. Configurar Variables de Entorno
Crear archivo `.env` en la raíz con tu API Key:
```env
OPENAI_API_KEY=tu_api_key_aqui
```

### 3. Ejecutar Demostración
```bash
python main.py
```
O ejecutar el script consolidado:
```bash
python patron_supervisor.py
```
