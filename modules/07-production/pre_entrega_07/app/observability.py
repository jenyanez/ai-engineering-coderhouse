"""Capa de observabilidad y trazado con OpenTelemetry y Arize Phoenix."""

import functools
import logging
import time
from typing import Any, Callable, Dict, Optional
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from app.config import settings

logger = logging.getLogger("Observability")
_tracer_initialized = False


def setup_observability() -> trace.Tracer:
    """Configura el TracerProvider de OpenTelemetry exportando hacia Arize Phoenix."""
    global _tracer_initialized
    if _tracer_initialized:
        return trace.get_tracer(settings.PHOENIX_PROJECT_NAME)

    try:
        resource = Resource.create({
            "service.name": settings.PHOENIX_PROJECT_NAME,
            "project.name": settings.PHOENIX_PROJECT_NAME,
        })
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=settings.PHOENIX_COLLECTOR_ENDPOINT)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _tracer_initialized = True
        logger.info(f"Observabilidad inicializada hacia {settings.PHOENIX_COLLECTOR_ENDPOINT}")
    except Exception as e:
        logger.warning(f"No se pudo conectar con colector Phoenix: {e}. Usando tracer por defecto.")
        trace.set_tracer_provider(TracerProvider())

    return trace.get_tracer(settings.PHOENIX_PROJECT_NAME)


tracer = setup_observability()


def trace_agent_span(agent_name: str, span_kind: str = "agent") -> Callable:
    """Decorador para instrumentar la ejecución de cada agente en el grafo."""
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with tracer.start_as_current_span(f"{agent_name}.execute") as span:
                start_time = time.time()
                span.set_attribute("openinference.span.kind", span_kind)
                span.set_attribute("agent.name", agent_name)

                # Extraer consulta o estado de entrada
                if args and isinstance(args[0], dict):
                    query = args[0].get("query", "")
                    span.set_attribute("input.value", str(query)[:500])

                try:
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start_time
                    span.set_attribute("execution.latency_seconds", elapsed)

                    if isinstance(result, dict):
                        span.set_attribute("output.value", str(result)[:500])
                    span.set_status(trace.StatusCode.OK)
                    return result
                except Exception as exc:
                    span.set_status(trace.StatusCode.ERROR, description=str(exc))
                    span.record_exception(exc)
                    raise exc

        return wrapper
    return decorator
