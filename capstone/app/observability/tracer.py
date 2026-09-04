"""Capa de observabilidad con OpenTelemetry y Arize Phoenix."""

import functools
import logging
import time
from typing import Any, Callable
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from app.config import settings

logger = logging.getLogger("Observability")
_tracer_initialized = False


def setup_observability() -> trace.Tracer:
    """Inicializa exportador OTLP apuntando al endpoint de Arize Phoenix."""
    global _tracer_initialized
    if _tracer_initialized:
        return trace.get_tracer(settings.phoenix_project_name)

    try:
        resource = Resource.create({
            "service.name": settings.phoenix_project_name,
            "project.name": settings.phoenix_project_name,
        })
        provider = TracerProvider(resource=resource)
        exporter = OTLPSpanExporter(endpoint=settings.phoenix_collector_endpoint)
        provider.add_span_processor(BatchSpanProcessor(exporter))
        trace.set_tracer_provider(provider)
        _tracer_initialized = True
        logger.info("Observabilidad activa hacia Phoenix.")
    except Exception as err:
        logger.warning(f"Phoenix no disponible ({err}), usando tracer local.")
        trace.set_tracer_provider(TracerProvider())

    return trace.get_tracer(settings.phoenix_project_name)


tracer = setup_observability()


def trace_agent_span(agent_name: str, span_kind: str = "agent") -> Callable:
    """Decorador para emitir spans con OpenInference hacia Phoenix."""

    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            with tracer.start_as_current_span(f"{agent_name}.execute") as span:
                start = time.perf_counter()
                span.set_attribute("openinference.span.kind", span_kind)
                span.set_attribute("agent.name", agent_name)

                if args and isinstance(args[0], dict):
                    span.set_attribute("input.query", str(args[0].get("query", ""))[:300])

                try:
                    res = func(*args, **kwargs)
                    span.set_attribute("latency_seconds", round(time.perf_counter() - start, 4))
                    span.set_status(trace.StatusCode.OK)
                    return res
                except Exception as err:
                    span.set_status(trace.StatusCode.ERROR, description=str(err))
                    span.record_exception(err)
                    raise err

        return wrapper

    return decorator
