# Unidad 2 · Escalabilidad Asíncrona con FastAPI y Redis

> **Programa:** AI Engineering — Coderhouse  
> **Módulo 7:** Producción y Robustez: Observabilidad, Costos y Despliegue  
> **Ejercicio:** Procesamiento Desacoplado con Colas de Mensajes y Patrón Polling  
> **Autor:** Jen Yanez  

---

## 📌 Lo Esencial en 3 Líneas

* **Qué construimos:** Una API REST con FastAPI que **no ejecuta el agente síncronamente dentro del request HTTP**, sino que lo encola en una lista de Redis y devuelve un `job_id` al instante (en milisegundos con status `202 Accepted`).
* **Por qué:** Los flujos de agentes y grafos de razonamiento tardan entre 30 y 120 segundos. Mantener una conexión HTTP abierta bloquea los workers de la API, agota los sockets del servidor y sufre timeouts por firewalls o proxies reversos.
* **El Patrón:** `Cliente` $\to$ `FastAPI` (Recibe y asigna Job ID) $\to$ `Redis` (Cola FIFO) $\to$ `Worker` (Ejecuta el grafo en background) $\to$ `Cliente` (Consulta periódica mediante Polling a `/status/{job_id}`).

---

## 🏗️ Arquitectura de la Solución

```
[ Cliente HTTP ]
       │
       │ 1. POST /process {"query": "..."}
       ▼
┌──────────────┐   2. SET status:job_id (pending)   ┌─────────────────┐
│   FastAPI    │ ─────────────────────────────────> │      Redis      │
│  (Gateway)   │   3. RPUSH tasks_queue (job_id)    │ (Message Broker │
│              │ ─────────────────────────────────> │   & Key-Value)  │
└──────────────┘                                    └─────────────────┘
       │                                                     ▲
       │ 4. Respuesta Inmediata (HTTP 202)                   │
       │    {"job_id": "...", "status": "pending"}          │
       ▼                                                     │ 5. BLPOP tasks_queue
[ Cliente HTTP ]                                             │    (Espera no bloqueante)
       │                                                     ▼
       │                                            ┌─────────────────┐
       │                                            │  Async Worker   │
       │                                            │ (LangGraph Run) │
       │                                            └─────────────────┘
       │                                                     │
       │                                                     │ 6. SET status:job_id
       │                                                     │    (processing -> completed)
       │                                                     ▼
       │ 7. GET /status/{job_id} (Polling)          ┌─────────────────┐
       └──────────────────────────────────────────> │      Redis      │
                                                    └─────────────────┘
```

---

## 🛠️ Componentes Implementados en `main.py`

1. **`POST /process` (El Recepcionista):**
   * Valida el payload con `Pydantic` (`TaskRequest`).
   * Genera un `job_id` criptográficamente único con `uuid.uuid4()`.
   * **Persiste primero el estado inicial (`pending`)** en Redis para prevenir condiciones de carrera si el worker lee antes de la escritura.
   * Encola el identificador en `tasks_queue` con `rpush`.
   * Retorna `TaskResponse` con código `202 Accepted` en $< 5\text{ ms}$.

2. **`GET /status/{job_id}` (Consulta de Estado):**
   * Recupera el documento JSON desde Redis con la clave `status:{job_id}`.
   * Si no existe, levanta una excepción `HTTPException(404)`.
   * Devuelve el estado actual (`pending`, `processing` o `completed`) junto con el payload de respuesta.

3. **`task_worker()` (El Especialista en Background):**
   * Bucle infinito asíncrono con `aioredis.blpop(QUEUE_NAME, timeout=2)`.
   * Actualiza el estado a `processing`.
   * Ejecuta el cómputo pesado o grafo multi-agente de forma desacoplada.
   * Almacena el resultado final bajo el estado `completed`.

4. **Gestión de Ciclo de Vida (`lifespan`):**
   * Utiliza el context manager moderno de FastAPI (`lifespan`) para inicializar el worker en el mismo bucle de eventos y cerrarlo limpiamente al apagar el servidor.

---

## 🚀 Guía de Ejecución Rápida

### 1. Iniciar Redis Server
```bash
# Opción A: Usando Homebrew (macOS)
brew services start redis

# Opción B: Usando Docker
docker run -d --name redis-local -p 6379:6379 redis:alpine
```

### 2. Instalar Dependencias
```bash
pip install -r requirements.txt
```

### 3. Iniciar la API y el Worker
```bash
python main.py
```
> La API quedará disponible en: `http://localhost:8000`  
> Documentación interactiva Swagger: `http://localhost:8000/docs`

### 4. Probar con el Cliente de Simulación (Polling)
En otra terminal:
```bash
python test_client.py
```

---

## 📊 Salida de Ejemplo del Polling

```text
============================================================
🚀 [Cliente] Iniciando prueba de Escalabilidad Asíncrona
============================================================

1. Enviando petición POST a /process...
   Query: '¿Cuál es el impacto financiero del mercado de IA en 2025?'
   Status Code: 202 (Accepted)
   Respuesta inmediata en: 4.12 ms
   Job ID recibido: 8f4c979d-3e3a-4467-91fa-40d9082723df
   Estado inicial: pending

2. Iniciando Polling sobre /status/8f4c979d-3e3a-4467-91fa-40d9082723df...
   [Intento 1] (1.0s) Estado: processing
   [Intento 2] (2.1s) Estado: processing
   [Intento 3] (3.2s) Estado: processing
   [Intento 4] (4.2s) Estado: completed

============================================================
🎉 TAREA COMPLETADA CON ÉXITO
============================================================
Resultado final:
'Análisis multi-agente completado exitosamente para: '¿Cuál es el impacto financiero del mercado de IA en 2025?''
Tiempo total transcurrido: 4.22 segundos
```
