# Módulo 7 — Producción y robustez: observabilidad, costos y despliegue

**5 unidades** | Estado: ✅ Completado

## Descripción

Preparación del sistema para producción mediante trazabilidad, observabilidad, evaluación, control de costos, supervisión humana, procesamiento asíncrono, APIs y despliegue.

## Contenidos y Ejercicios

### Unidad 1 — Observabilidad y Trazado: Arize Phoenix y LangSmith
* **Ejercicio:** Instrumentación de un sistema multi-agente con OpenTelemetry/OpenInference, análisis de jerarquía de spans en Arize Phoenix, descomposición de latencias, evaluación de grounding y optimización de costos de tokens.
* **Ubicación:** [`01_observabilidad_trazado/`](./01_observabilidad_trazado/)
  * [Informe Técnico de Observabilidad (`README.md`)](./01_observabilidad_trazado/README.md)
  * [Informe Web Interactivo (`informe_observabilidad_phoenix.html`)](./01_observabilidad_trazado/informe_observabilidad_phoenix.html)
  * [Configuración OpenTelemetry (`tracer_setup.py`)](./01_observabilidad_trazado/tracer_setup.py)
  * [Generador de Tráfico y Benchmark (`traffic_generator.py`)](./01_observabilidad_trazado/traffic_generator.py)
  * [Suite de Pruebas Automatizadas (`test_observability.py`)](./01_observabilidad_trazado/test_observability.py)

### Unidad 2 — Escalabilidad Asíncrona con FastAPI y Redis
* **Ejercicio:** Arquitectura de procesamiento desacoplado con colas FIFO en Redis, patrón de sondeo (Polling), ciclo de vida completo de tareas y worker en background resiliente.
* **Ubicación:** [`02_escalabilidad_asincrona/`](./02_escalabilidad_asincrona/)
  * [Documentación Técnica (`README.md`)](./02_escalabilidad_asincrona/README.md)
  * [Servicio FastAPI + Worker (`main.py`)](./02_escalabilidad_asincrona/main.py)
  * [Script de Simulación de Polling (`test_client.py`)](./02_escalabilidad_asincrona/test_client.py)
  * [Suite de Pruebas Unitarias de Evaluación (`test_evaluation.py`)](./02_escalabilidad_asincrona/test_evaluation.py)

## Entregable Principal

### 🚀 Pre-Entrega 07 — API de Producción y Monitoreo Activo
* **Ubicación:** [`pre_entrega_07/`](./pre_entrega_07/)
  * [Documentación Técnica y Arquitectura Macro-a-Micro (`README.md`)](./pre_entrega_07/README.md)
  * [API Asíncrona FastAPI (`app/main.py`)](./pre_entrega_07/app/main.py)
  * [Worker con Persistencia Redis (`app/worker.py`)](./pre_entrega_07/app/worker.py)
  * [Orquestador LangGraph con Checkpointer (`app/graph.py`)](./pre_entrega_07/app/graph.py)
  * [Controlador Human-in-the-Loop (`app/hitl.py`)](./pre_entrega_07/app/hitl.py)
  * [Observabilidad con Arize Phoenix (`app/observability.py`)](./pre_entrega_07/app/observability.py)
  * [Suite de Pruebas Automatizadas (`tests/test_api.py`)](./pre_entrega_07/tests/test_api.py)
  * [Benchmark de 5 Peticiones Concurrentes (`tests/benchmark_concurrent.py`)](./pre_entrega_07/tests/benchmark_concurrent.py)
  * [Evidencia de Observabilidad (`screenshots/`)](./pre_entrega_07/screenshots/)
  * [Contenerización con Docker Compose (`docker-compose.yml`)](./pre_entrega_07/docker-compose.yml)
