import logging
import structlog
from .config import Settings

def setup_logging(level: str = "INFO", mask_pii: bool = True):
    processors = [
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer(),
    ]
    structlog.configure(
        processors=processors,  # type: ignore[arg-type]
        logger_factory=structlog.stdlib.LoggerFactory(),
    )
    logging.basicConfig(level=getattr(logging, level.upper(), logging.INFO))

def setup_tracing_if_enabled(s: Settings):
    if not s.OTEL_EXPORTER_OTLP_ENDPOINT:
        return
    try:
        from opentelemetry import trace
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace.export import BatchSpanProcessor
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

        resource = Resource.create({"service.name": "rag-min-prod"})
        provider = TracerProvider(resource=resource)
        processor = BatchSpanProcessor(OTLPSpanExporter(endpoint=s.OTEL_EXPORTER_OTLP_ENDPOINT))
        provider.add_span_processor(processor)
        trace.set_tracer_provider(provider)
    except Exception as e:
        print(f"[otel] failed to init tracing: {e}")
