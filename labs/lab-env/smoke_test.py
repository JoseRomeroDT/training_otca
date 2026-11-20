"""Prueba de humo del entorno de laboratorio (Laboratorio 0).

Envía por OTLP gRPC (localhost:4317) un span, una métrica y un log con
service.name = "smoke-test". Después búscalos en Jaeger, Prometheus y en los
logs del Collector.

Ejecutar: python labs/lab-env/smoke_test.py
"""
import logging
import os

from opentelemetry import metrics, trace
from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
resource = Resource.create({SERVICE_NAME: "smoke-test"})

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=ENDPOINT, insecure=True)))

meter_provider = MeterProvider(
    resource=resource,
    metric_readers=[PeriodicExportingMetricReader(OTLPMetricExporter(endpoint=ENDPOINT, insecure=True))],
)

logger_provider = LoggerProvider(resource=resource)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(OTLPLogExporter(endpoint=ENDPOINT, insecure=True)))
set_logger_provider(logger_provider)
logger = logging.getLogger("smoke-test")
logger.setLevel(logging.INFO)
logger.addHandler(LoggingHandler(level=logging.INFO, logger_provider=logger_provider))

tracer = tracer_provider.get_tracer("lab00.smoke")
counter = meter_provider.get_meter("lab00.smoke").create_counter("smoke.runs", unit="{run}", description="Ejecuciones de la prueba de humo")

with tracer.start_as_current_span("prueba-de-humo") as span:
    span.set_attribute("lab.paso", "laboratorio-0")
    counter.add(1)
    logger.info("Prueba de humo enviada por OTLP")
    trace_id = format(span.get_span_context().trace_id, "032x")

# shutdown() vacía los lotes pendientes antes de salir.
tracer_provider.shutdown()
meter_provider.shutdown()
logger_provider.shutdown()

print(f"Enviado a {ENDPOINT}: 1 span, 1 métrica y 1 log del servicio 'smoke-test'.")
print(f"trace_id = {trace_id}")
print("Búscalo en Jaeger (servicio smoke-test), en Prometheus (smoke_runs_total)")
print("y en los logs del Collector: docker logs otel-collector 2>&1 | grep -i 'prueba de humo'")
