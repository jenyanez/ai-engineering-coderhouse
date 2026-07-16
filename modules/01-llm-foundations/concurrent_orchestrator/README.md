# Clase 1: Arquitectura Asíncrona con Python 3.12
## Orquestador Concurrente de Modelos LLM

Este proyecto implementa las simulaciones de llamadas concurrentes a APIs de modelos de lenguaje (LLM) utilizando las características asíncronas de Python 3.12.

### Objetivos de Aprendizaje Cubiertos

1. **Diferenciación de tareas I/O-bound y CPU-bound:**
   - **I/O-Bound (Llamadas a APIs, consultas de base de datos):** La mayor parte del tiempo se pasa esperando una respuesta de la red. Es aquí donde `asyncio` brilla, permitiendo que un único hilo procese cientos de solicitudes concurrentes al liberar el control mientras espera.
   - **CPU-Bound (Cálculo de embeddings local, inferencia local con PyTorch, limpieza de datos con Pandas):** Tareas que consumen ciclos de CPU intensivos. Si se ejecutan directamente en una corrutina de `asyncio`, bloquearán el *Event Loop* paralizando a todos los usuarios. En estos casos, se deben delegar a un hilo separado con `asyncio.to_thread()` o usar `multiprocessing`.

2. **Concurrencia con `asyncio.gather` y `asyncio.TaskGroup`:**
   - Implementamos `asyncio.gather` para el disparo y recolección simultánea clásica.
   - Añadimos la sintaxis moderna de `asyncio.TaskGroup` (Python 3.11+) como alternativa moderna y más segura para el control de excepciones (si una tarea falla, cancela el resto automáticamente).

3. **Control de Flujo con Semáforos (`asyncio.Semaphore`):**
   - Limitación de concurrencia máxima a 2 peticiones activas simultáneas sobre un lote de 10 tareas para evitar saturar las APIs y prevenir errores `429: Too Many Requests`.

4. **Resiliencia y Timeouts (`asyncio.timeout`):**
   - Control de latencia máxima con `asyncio.timeout(2.0)` para cancelar automáticamente llamadas colgadas sin detener el flujo general del backend.

---

### Estructura Modular (Decoupled Architecture)

El código sigue estrictamente un patrón desacoplado y modular:
- `main.py`: Punto de entrada que coordina y ejecuta las simulaciones.
- `models/llm_simulators.py`: Simulación de las APIs de LLM utilizando `asyncio.sleep()`.
- `orchestrator/concurrent_runner.py`: Implementación de los patrones de concurrencia (`gather`, `TaskGroup`, `Semaphore`, `timeout`).
- `utils/logger.py`: Configuración de logs con timestamps de alta resolución.

---

### Requisitos y Ejecución

* **Requisitos:** Python 3.12+ (sin librerías de terceros necesarias).

Para ejecutar las simulaciones y observar la concurrencia en tiempo real:

```bash
python main.py
```