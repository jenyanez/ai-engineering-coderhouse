# Módulo 6 — Sistemas multiagente: colaboración y especialización

**7 unidades** | Estado: 🔄 En progreso

## Descripción

Diseño de sistemas en los que múltiples agentes especializados colaboran, delegan tareas y son coordinados mediante patrones como supervisor y jerarquías.

## Contenidos y Ejercicios

### Unidad 1 — Topologías Multi-Agente: Colaboración vs Jerarquía
* **Ejercicio:** Propuesta arquitectónica de un sistema multi-agente jerárquico (Patrón Supervisor) para atención de quejas de e-commerce en Twitter/X.
* **Ubicación:** [`01_topologias_multiagente/`](./01_topologias_multiagente/)
  * [Propuesta Técnica en Markdown (`propuesta_arquitectura.md`)](./01_topologias_multiagente/propuesta_arquitectura.md)

### Unidad 2 — El Patrón Supervisor: Delegación Dinámica
* **Ejercicio:** Implementación de un grafo supervisor con ruteo dinámico hacia agentes especialistas (*Analista* y *Escritor*) en LangGraph.
* **Ubicación:** [`02_patron_supervisor/`](./02_patron_supervisor/)
  * [Código del Ejercicio (`patron_supervisor.py`)](./02_patron_supervisor/patron_supervisor.py)
  * [Documentación y Topología (`README.md`)](./02_patron_supervisor/README.md)

### Unidad 3 — Estado Compartido y Comunicación Asíncrona
* **Ejercicio:** Manejo de estado inmutable, contratos tipados con Pydantic V2 y optimización con concurrencia real (`asyncio.gather`).
* **Ubicación:** [`03_estado_compartido_asincrono/`](./03_estado_compartido_asincrono/)
  * [Código del Ejercicio (`estado_compartido_asincrono.py`)](./03_estado_compartido_asincrono/estado_compartido_asincrono.py)
  * [Documentación y Concurrencia (`README.md`)](./03_estado_compartido_asincrono/README.md)

## Entregable

* **Pre-Entrega 6:** Orquestador Multi-Agente de Análisis e Investigación con Topología Jerárquica, Supervisor inteligente, búsqueda semántica en ChromaDB (`text-embedding-3-small`), cómputo cuantitativo de CAGR y síntesis ejecutiva.
* **Ubicación:** [`pre_entrega_06/`](./pre_entrega_06/)
  * [Documentación Técnica y Diagrama Mermaid (`README.md`)](./pre_entrega_06/README.md)
  * [Notebook Demostrativo Interactivo (`demo.ipynb`)](./pre_entrega_06/demo.ipynb)
  * [Suite de Pruebas Automatizadas (`test_orchestrator.py`)](./pre_entrega_06/test_orchestrator.py)
