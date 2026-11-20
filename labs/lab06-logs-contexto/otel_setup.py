"""Lab 6 · Configuración común del SDK para trazas y logs (OTLP gRPC → Collector).

Logs: Python no usa una "Logs API" para la aplicación. Se usa el módulo estándar
`logging` y el SDK le agrega un handler (LoggingHandler, el "logs bridge") que
convierte cada registro en un LogRecord de OpenTelemetry con el trace_id y el
span_id del span activo.

Fuentes:
  https://opentelemetry.io/docs/languages/python/instrumentation/#logs
  https://opentelemetry.io/docs/concepts/signals/logs/
"""
import logging
import os

from opentelemetry import trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")


def configurar_otel(service_name):
    """Configura trazas y logs; devuelve (tracer, logger)."""
    resource = Resource.create({SERVICE_NAME: service_name})

    tracer_provider = TracerProvider(resource=resource)
    tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)))
    trace.set_tracer_provider(tracer_provider)

    logger_provider = LoggerProvider(resource=resource)
    logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=OTLP_ENDPOINT, insecure=True)))
    set_logger_provider(logger_provider)

    # Logs bridge: todo lo que pase por `logging` (nivel INFO o más) también sale por OTLP.
    logging.basicConfig(level=logging.INFO)
    logging.getLogger().addHandler(LoggingHandler(level=logging.INFO, logger_provider=logger_provider))
    # Menos ruido: los logs de acceso del servidor de desarrollo de Flask solo desde WARNING.
    logging.getLogger("werkzeug").setLevel(logging.WARNING)

    return trace.get_tracer(f"lab06.{service_name}"), logging.getLogger(service_name)
