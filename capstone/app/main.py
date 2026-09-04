"""Punto de entrada principal de la aplicación FastAPI con Lifespan asíncrono."""

import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from app.api.routes import router as api_router
from app.api.worker import background_worker_loop
from app.data.ingestion import run_ingestion_pipeline
from app.ui.dashboard import ui_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ciclo de vida asíncrono de la aplicación: inicialización y apagado limpio."""
    # 1. Ingesta inicial de la base de conocimiento vectorial
    try:
        res = run_ingestion_pipeline()
        print(f"✅ Ingesta inicial completada: {res['chunks']} fragmentos en ChromaDB.")
    except Exception as err:
        print(f"⚠️ Ingesta omitida o diferida: {err}")

    # 2. Iniciar Worker en background para consumo de colas FIFO
    worker_task = asyncio.create_task(background_worker_loop())

    yield

    # Apagado ordenado
    worker_task.cancel()
    try:
        await worker_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Sistema Intelligence de Grado de Producción",
    description="Orquestador multi-agente, RAG híbrido, Redis y observabilidad con Arize Phoenix",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Registro de routers
app.include_router(api_router)
app.include_router(ui_router)


@app.get("/", include_in_schema=False)
async def root_redirect():
    """Redirección automática hacia la consola Mission Control."""
    return RedirectResponse(url="/dashboard")


if __name__ == "__main__":
    import uvicorn
    from app.config import settings

    uvicorn.run("app.main:app", host=settings.host, port=settings.port, reload=True)
