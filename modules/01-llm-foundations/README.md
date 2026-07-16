# Módulo 1 — La interfaz base: conexión y abstracción de LLMs

**6 unidades** | Estado: ✅ Completado

## Descripción

Construcción de una capa base para interactuar con modelos de lenguaje utilizando Python 3.12, `asyncio` y SDKs oficiales.

## Objetivos de aprendizaje

- Diferenciar entre tareas I/O-bound y CPU-bound en el contexto de aplicaciones de IA.
- Implementar llamadas concurrentes a múltiples APIs de LLM utilizando `asyncio.gather` y `TaskGroups`.
- Gestionar la latencia y los límites de tasa (rate limits) mediante timeouts y semáforos asíncronos.
- Evitar errores comunes de bloqueo del event loop en Python 3.12.

## Conceptos principales

- Corrutinas con `async def`
- Esperas no bloqueantes con `await`
- Event loop y tareas
- Ejecución concurrente con `asyncio.gather()`
- Gestión de timeouts con `asyncio.timeout()`
- Control de concurrencia mediante `asyncio.Semaphore()`
- Streaming de tokens
- Prevención de operaciones bloqueantes

## Entregable

**Orquestador Concurrente de Modelos LLM** — Simulación de llamadas concurrentes a APIs de modelos de lenguaje.

### Rúbrica de evaluación

| Criterio | Descripción | Peso |
|---|---|---|
| Implementación de Asincronía y No Bloqueo | Uso correcto de async/await y evitación de funciones bloqueantes como `time.sleep` | 30% |
| Gestión de Concurrencia con asyncio.gather | Capacidad para orquestar llamadas simultáneas y procesar resultados de forma colectiva | 25% |
| Control de Flujo con Semáforos | Uso de `asyncio.Semaphore` para limitar el consumo de recursos y prevenir la saturación | 25% |
| Resiliencia y Manejo de Timeouts | Implementación de límites de tiempo y captura de excepciones para garantizar la estabilidad | 20% |
