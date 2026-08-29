import asyncio, json, os, time, uuid
from contextlib import asynccontextmanager
from enum import Enum
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel, Field
from redis import asyncio as aioredis

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
QUEUE_NAME = os.getenv("QUEUE_NAME", "tasks_queue")
STATUS_PREFIX = os.getenv("STATUS_PREFIX", "status:")

redis_client = aioredis.from_url(REDIS_URL, decode_responses=True)


class TaskStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class TaskRequest(BaseModel):
    query: str = Field(..., min_length=3, description="Consulta para el agente")


class TaskResponse(BaseModel):
    job_id: str
    status: TaskStatus
    message: str


class JobStatusResponse(BaseModel):
    job_id: str
    status: TaskStatus
    query: str
    result: Optional[str] = None
    error: Optional[str] = None
    created_at: float
    updated_at: float
    execution_time: Optional[float] = None


async def task_worker():
    """Worker en segundo plano para procesar tareas de la cola de Redis."""
    print("🚀 [Worker] Iniciado y a la escucha de tareas...")
    while True:
        try:
            task = await redis_client.blpop(QUEUE_NAME, timeout=2)
            if task is None:
                continue
            _, job_id = task
            raw_data = await redis_client.get(f"{STATUS_PREFIX}{job_id}")
            if not raw_data:
                continue

            job = json.loads(raw_data)
            job["status"] = TaskStatus.PROCESSING
            job["updated_at"] = time.time()
            await redis_client.set(f"{STATUS_PREFIX}{job_id}", json.dumps(job))

            try:
                await asyncio.sleep(3)  # Simula ejecución pesada de LangGraph
                job["status"] = TaskStatus.COMPLETED
                job["result"] = f"Respuesta del agente para: '{job.get('query')}'"
                job["updated_at"] = time.time()
                job["execution_time"] = round(job["updated_at"] - job["created_at"], 2)
            except Exception as inner_err:
                job["status"] = TaskStatus.FAILED
                job["error"] = str(inner_err)
                job["updated_at"] = time.time()

            await redis_client.set(f"{STATUS_PREFIX}{job_id}", json.dumps(job))
            print(f"✅ [Worker] Tarea {job_id} -> {job['status']}")
        except asyncio.CancelledError:
            print("🛑 [Worker] Detenido limpiamente.")
            break
        except Exception as err:
            print(f"⚠️ [Worker] Error en cola: {err}")
            await asyncio.sleep(1)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Gestión del ciclo de vida del worker junto a FastAPI."""
    worker_task = asyncio.create_task(task_worker())
    yield
    worker_task.cancel()
    await redis_client.aclose()


app = FastAPI(
    title="API Asíncrona con FastAPI y Redis",
    description="Procesamiento desacoplado con colas y polling.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.post("/process", response_model=TaskResponse, status_code=status.HTTP_202_ACCEPTED)
async def create_task(request: TaskRequest):
    """Recibe la consulta, genera el Job ID, persiste el estado y encola la tarea."""
    job_id = str(uuid.uuid4())
    now = time.time()
    initial_job = {
        "job_id": job_id,
        "status": TaskStatus.PENDING,
        "query": request.query,
        "result": None,
        "error": None,
        "created_at": now,
        "updated_at": now,
        "execution_time": None,
    }
    await redis_client.set(f"{STATUS_PREFIX}{job_id}", json.dumps(initial_job))
    await redis_client.rpush(QUEUE_NAME, job_id)
    return TaskResponse(
        job_id=job_id,
        status=TaskStatus.PENDING,
        message="Tarea encolada. Consulta /status/{job_id} para ver el resultado.",
    )


@app.get("/status/{job_id}", response_model=JobStatusResponse)
async def get_status(job_id: str):
    """Consulta el estado y resultado del job_id en Redis."""
    raw_data = await redis_client.get(f"{STATUS_PREFIX}{job_id}")
    if not raw_data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"No se encontró ninguna tarea con el Job ID: {job_id}",
        )
    return json.loads(raw_data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=False)
