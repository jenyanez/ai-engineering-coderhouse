"""Módulo de configuración e inicialización de trazabilidad OpenInference / OpenTelemetry con Arize Phoenix y LangSmith."""

import os
from pathlib import Path
from dotenv import load_dotenv
from openinference.instrumentation.langchain import LangChainInstrumentor
from openinference.instrumentation.openai import OpenAIInstrumentor
from phoenix.otel import register

# Cargar variables de entorno
load_dotenv(Path(__file__).resolve().parent / ".env")


def init_tracing() -> bool:
    """Inicializa los exportadores de OpenTelemetry para Arize Phoenix y activa LangSmith.
    
    Returns:
        bool: True si la inicialización se completó correctamente.
    """
    endpoint = os.getenv("PHOENIX_COLLECTOR_ENDPOINT", "http://127.0.0.1:6006/v1/traces")
    project_name = os.getenv("PHOENIX_PROJECT_NAME", "modulo-7-observabilidad")
    
    try:
        # 1. Registrar TracerProvider de Phoenix
        tracer_provider = register(
            project_name=project_name,
            endpoint=endpoint,
            set_global_tracer_provider=True
        )
        
        # 2. Instrumentar SDK de OpenAI
        OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
        
        # 3. Instrumentar LangChain y LangGraph (captura grafos, agentes y herramientas RAG)
        LangChainInstrumentor().instrument(tracer_provider=tracer_provider)
        
        print(f"🔥 [Arize Phoenix] Trazabilidad activa -> Proyecto: '{project_name}' | Endpoint: {endpoint}")
        
        # 4. Notificar estado de LangSmith si está configurado
        if os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true":
            ls_proj = os.getenv("LANGCHAIN_PROJECT", "default")
            print(f"🦜🛠️ [LangSmith] Trazabilidad paralela activa -> Proyecto: '{ls_proj}'")
            
        return True
    except Exception as exc:
        print(f"⚠️ [Observabilidad] Advertencia al registrar trazador: {exc}")
        return False


if __name__ == "__main__":
    init_tracing()
