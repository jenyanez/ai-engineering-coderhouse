# 🚀 Pre-Entrega 07 — API de Producción y Monitoreo Activo

> **Curso:** AI Engineering · Coderhouse  
> **Módulo 7:** Producción y Robustez: Observabilidad, Costos y Despliegue  
> **Autor:** Jen Yanez  
> **Estado:** ✅ Completado y Validado (100% Pruebas Pasando)

---

## 🗺️ 1. Visión Macro a Micro: Evolución Incremental del Sistema

```
========================================================================================================
                                     ÁRBOL EVOLUTIVO DEL PROYECTO
========================================================================================================

  [ MÓDULO 3 ] Ingesta y Base Vectorial
      ├── Chunking semántico por tokens (tiktoken, NFKC, overlap)
      └── Persistencia en ChromaDB (distancia coseno, IDs deterministas SHA-256)
             │
             ▼
  [ MÓDULO 5 ] Evaluación RAG y Grounding
      ├── Métricas de recuperación (Context Precision, Recall)
      └── Prevención de alucinaciones y grounding en documentos
             │
             ▼
  [ MÓDULO 6 ] Orquestación Multi-Agente
      ├── Grafo jerárquico LangGraph (Supervisor, Investigador, Analista, Sintetizador)
      └── Especialización de roles y contratos de estado tipados
             │
             ▼
  [ MÓDULO 7 ] API de Producción, Observabilidad y Gobernanza (ESTE ENTREGABLE)
      ├── ⚡ Endpoints Asíncronos No Bloqueantes (FastAPI + HTTP 202 Accepted en ~5ms)
      ├── 💾 Persistencia de Estado y Checkpoints (Redis con TTL 24h + Fallback Durable en Disco)
      ├── 📊 Observabilidad Activa y Métricas (Arize Phoenix + OpenTelemetry OTLP)
      ├── 👤 Gobernanza Human-in-the-Loop (Pausa de seguridad y aprobación humana interactiva)
      ├── 🛡️ Guardrails de Seguridad (Bloqueo de Prompt Injection en 0.1ms sin costo de tokens)
      ├── 💰 Auditoría FinOps (Cálculo exacto de costos y tokens en USD en tiempo real)
      └── 🎛️ Mission Control Dashboard (Interfaz web oscura interactiva en `/dashboard`)
========================================================================================================
```

---

## 🏗️ 2. Arquitectura Global Unificada

```
                              ┌──────────────────────────────────────────────────────────┐
                              │                    CLIENTES Y USUARIOS                   │
                              │   Web UI / Slack Bot / App Móvil / Swagger UI / Scripts  │
                              └────────────────────────────┬─────────────────────────────┘
                                                           │
                                                           │ HTTP POST /tasks (Query)
                                                           ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                       CAPA API (FastAPI - app/main.py)                                  │
│                                                                                                         │
│  1. 🛡️ Guardrails Filter (app/guardrails.py): Valida ataques/inyecciones en 0.1ms (0 tokens)           │
│  2. ⚡ Dispatch Inmediato: Genera job_id (#job_15e9...) y retorna HTTP 202 Accepted en < 10ms          │
│  3. 🎛️ Mission Control Dashboard: Servido en GET /dashboard con visor interactivo de informes         │
└──────────────────────────────────────────────┬──────────────────────────────────────────────────────────┘
                                               │
                                               │ BackgroundTasks
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                  CAPA WORKER Y PERSISTENCIA (app/worker.py & app/store.py)              │
│                                                                                                         │
│  • TaskStore: Almacén de ciclo de vida (PENDING ➔ RUNNING ➔ WAITING_APPROVAL ➔ COMPLETED / FAILED)     │
│  • Redis 7: Persistencia primaria con TTL de 24h (ex=86400).                                            │
│  • Disco JSON Durable (data/persistent_tasks.json): Fallback permanente contra reinicios de servidor.  │
│  • FinOps Auditor (app/finops.py): Cálculo de tokens y costo financiero exacto en USD.                 │
└──────────────────────────────────────────────┬──────────────────────────────────────────────────────────┘
                                               │
                                               │ Invoca
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                            ORQUESTADOR MULTI-AGENTE (LangGraph - app/graph.py)                          │
│                                                                                                         │
│                     ┌──────────────────────────────────────────────┐                                    │
│                     │           🎯 Supervisor Jerárquico           │                                    │
│                     └──────┬────────────────────────────────┬──────┘                                    │
│                            │                                │                                           │
│              Rutea         ▼                                ▼         Rutea                             │
│       ┌──────────────────────────────┐            ┌──────────────────────────────┐                      │
│       │  🔍 Investigador (RAG / KB)  │            │    📈 Analista Cuantitativo   │                      │
│       │  • ChromaDB Knowledge Base   │            │    • Cálculo financiero CAGR │                      │
│       │  • Grounding & Detección KB  │            │    • Modelado de crecimiento │                      │
│       └──────────────────────────────┘            └──────────────────────────────┘                      │
│                                                                                                         │
│                                              │                                                          │
│                                              ▼                                                          │
│                     ┌──────────────────────────────────────────────┐                                    │
│                     │       🛑 Nodo Human-in-the-Loop (HITL)        │                                    │
│                     │  Pausa el grafo en WAITING_APPROVAL          │                                    │
│                     │  Espera POST /tasks/{id}/approve             │                                    │
│                     └──────────────────────┬───────────────────────┘                                    │
│                                            │                                                            │
│                              Reanudación tras aprobación                                                │
│                                            ▼                                                            │
│                     ┌──────────────────────────────────────────────┐                                    │
│                     │         📝 Sintetizador Ejecutivo            │                                    │
│                     │   Redacta informe final fundamentado         │                                    │
│                     └──────────────────────────────────────────────┘                                    │
└──────────────────────────────────────────────┬──────────────────────────────────────────────────────────┘
                                               │
                                               │ Exportación OTLP (Trazas, Spans, Tokens)
                                               ▼
┌─────────────────────────────────────────────────────────────────────────────────────────────────────────┐
│                                OBSERVABILIDAD ACTIVA (Arize Phoenix - Puerto 6006)                       │
│  • Spans jerárquicos de cada agente con atributos OpenInference.                                        │
│  • Cascada de latencias (Waterfall), consumo de tokens y evaluación de precisión.                       │
└─────────────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

## 📁 3. Estructura Modular del Proyecto

Todos los módulos siguen el patrón de **Arquitectura Desacoplada** y cumplen estrictamente con la regla de **$< 150$ líneas de código por archivo**:

```text
pre_entrega_07/
├── app/
│   ├── __init__.py               # Paquete principal
│   ├── config.py                 # (50 líneas) Configuración Pydantic Settings y variables .env
│   ├── state.py                  # (77 líneas) Esquemas Pydantic y tipado AgentState
│   ├── guardrails.py             # (37 líneas) Filtro heurístico contra Prompt Injection (0 tokens)
│   ├── finops.py                 # (42 líneas) Auditoría de costos de tokens en USD y ahorro
│   ├── observability.py          # (76 líneas) OpenTelemetry Tracer y exportador hacia Arize Phoenix
│   ├── graph.py                  # (130 líneas) Grafo LangGraph jerárquico con grounding y HITL
│   ├── hitl.py                   # (29 líneas) Evaluador de operaciones críticas y resúmenes
│   ├── store.py                  # (90 líneas) Persistencia Redis con fallback durable en disco JSON
│   ├── worker.py                 # (83 líneas) Procesador asíncrono en background y captura FAILED
│   ├── dashboard_view.py         # (144 líneas) Generador HTML de la interfaz Mission Control
│   └── main.py                   # (119 líneas) API FastAPI (POST /tasks, GET /tasks, /approve, /dashboard)
├── data/
│   ├── chroma_db/                # Base vectorial persistente ChromaDB (Módulo 3)
│   ├── knowledge_documents/      # Documentos fuente Markdown (IA, Mercados, RAG, Multi-Agentes)
│   └── persistent_tasks.json     # Base de datos persistente JSON durable en disco
├── screenshots/                  # Capturas reales de trazabilidad y métricas en Phoenix
│   ├── phoenix_dashboard.png     # Dashboard general de trazas
│   ├── phoenix_spans.png         # Cascada de spans por agente
│   ├── phoenix_trace_detail.png  # Detalle de ejecución del sintetizador
│   └── phoenix_cost_tokens.png   # Gráfica de dispersión de latencia y tokens
├── tests/
│   ├── __init__.py               # Paquete de pruebas
│   ├── test_api.py               # (116 líneas) Suite de 9 pruebas automatizadas (100% passing)
│   └── benchmark_concurrent.py   # (89 líneas) Benchmark de 5 peticiones concurrentes
├── docker-compose.yml            # Orquestación multicontenedor con healthchecks y red bridge
├── Dockerfile                    # Contenedor de producción Python 3.12
├── requirements.txt              # Dependencias fijadas del proyecto
├── .env.example                  # Plantilla de variables de entorno seguras
└── README.md                     # Documentación técnica integral
```

---

## 🚀 4. Guía de Ejecución Rápida

### Opción A: Despliegue con Docker Compose (Recomendado)

Levanta la arquitectura completa (FastAPI + Redis 7 + Arize Phoenix) con un solo comando:

```bash
# 1. Configurar variables de entorno
cp .env.example .env

# 2. Construir y levantar todos los servicios
docker compose up -d --build

# 3. Verificar estado de los contenedores
docker compose ps
```

* **Dashboard Web:** `http://localhost:8000/dashboard`
* **Swagger UI:** `http://localhost:8000/docs`
* **Arize Phoenix:** `http://localhost:6006`

---

### Opción B: Ejecución en Local (Python Virtualenv)

```bash
# 1. Instalar dependencias
pip install -r requirements.txt

# 2. Iniciar servidor Arize Phoenix (en una terminal)
python -m phoenix.server.main serve

# 3. Iniciar API FastAPI con Uvicorn (en otra terminal)
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

---

## 🧪 5. Suite de Pruebas y Validación Automatizada

Ejecutar la suite completa de pruebas unitarias y de integración:

```bash
python -m unittest tests/test_api.py -v
```

### Resultados de la Suite (9/9 Pasando al 100%):
```text
test_01_health_check ... ok (Health check operativo y estado de servicios)
test_02_create_task_async_202 ... ok (HTTP 202 Accepted encolado instantáneo con job_id)
test_03_hitl_approval_lifecycle ... ok (Ciclo completo: WAITING_APPROVAL -> POST /approve -> COMPLETED)
test_04_hitl_rejection_lifecycle ... ok (Rechazo humano controlado en nodo HITL -> REJECTED)
test_05_task_not_found ... ok (Manejo 404 ante ID no existente)
test_06_invalid_approval_on_non_waiting_task ... ok (Manejo 400 ante estados inconsistentes)
test_07_list_tasks ... ok (Consulta global y paginada de tareas)
test_08_guardrails_blocks_injection ... ok (Bloqueo exitoso de Prompt Injection en 0.1ms)
test_09_dashboard_html ... ok (Renderizado y servicio de la UI Mission Control)

----------------------------------------------------------------------
Ran 9 tests in 0.256s (OK - 100% de éxito)
```

---

## ⚡ 6. Benchmark de Concurrencia (5 Peticiones Simultáneas)

Ejecutar el benchmark asíncrono:

```bash
python tests/benchmark_concurrent.py
```

### Resultados del Benchmark:
```text
================================================================================
🚀 RESULTADOS DEL BENCHMARK CONCURRENTE
================================================================================
Job ID             | Consulta                                 | Latencia HTTP  | Estado
-------------------------------------------------------------------------------------
job_95d4928dda63   | Proyección y CAGR del mercado de IA...   | 14.69ms        | ✅ COMPLETED
job_d52f6cca8e5e   | Tasa de adopción de IA en empresas ...   | 3.93ms         | ✅ COMPLETED
job_5f458f37a716   | Riesgos operativos y gobernanza en ...   | 3.42ms         | ✅ COMPLETED
job_71a019620e35   | Métricas de precisión y latencia en...   | 3.23ms         | ✅ COMPLETED
job_914c10334f7c   | Impacto de la orquestación jerárqui...   | 3.67ms         | ✅ COMPLETED
================================================================================
⏱️ Tiempo total de encolamiento (5 tareas): 29.01ms (Promedio: 5.80ms/req)
🎯 Conclusión: Arquitectura 100% no bloqueante. Las 5 solicitudes fueron aceptadas en < 50ms.
```

---

## 🛡️ 7. Seguridad y Buenas Prácticas

1. **Credenciales Seguras:** Prohibición absoluta de API Keys hardcodeadas. Uso de `.env.example` y variables de entorno del sistema.
2. **Defensa en Profundidad:** Los **Guardrails** filtran inyecciones antes de consumir recursos de cómputo.
3. **Persistencia Resiliente:** Los estados nunca se pierden gracias al almacenamiento en disco JSON durable y Redis.
4. **Respuesta Grounded:** Si una consulta no está en la Base de Conocimiento (ej. el clima), el sistema informa transparentemente sus dominios especializados sin alucinar datos.
