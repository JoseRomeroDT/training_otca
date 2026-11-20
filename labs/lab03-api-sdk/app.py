"""Lab 3 · Instrumentación manual con la API y el SDK (salida a consola).

- El SDK se configura UNA vez al inicio: Resource + TracerProvider + MeterProvider.
- El código de negocio solo usa la API: trace.get_tracer / metrics.get_meter.
- Composición y extensión: el TracerProvider tiene DOS span processors, uno de
  ellos escrito por nosotros (ContadorDeSpans).

Fuentes:
  https://opentelemetry.io/docs/languages/python/instrumentation/
  https://opentelemetry.io/docs/languages/python/exporters/#console

Ejecutar: flask run -p 8080   (y en otra terminal: curl localhost:8080/rolldice)
"""
from random import randint

from flask import Flask

from opentelemetry import metrics, trace
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import SpanProcessor, TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter


class ContadorDeSpans(SpanProcessor):
    """Span processor propio: el SDK es extensible mediante interfaces."""

    def __init__(self):
        self.total = 0

    def on_end(self, span):
        self.total += 1
        print(f"[ContadorDeSpans] terminó '{span.name}' (total: {self.total})", flush=True)


# ── 1. Configuración del SDK (una sola vez, al iniciar el proceso) ──────────
resource = Resource.create({SERVICE_NAME: "dice-server", SERVICE_VERSION: "1.0.0"})

tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(ContadorDeSpans())
tracer_provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(tracer_provider)

# El intervalo por defecto es 60000 ms; aquí 10 s para ver resultados rápido.
metric_reader = PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=10_000)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[metric_reader]))

# ── 2. Instrumentación con la API (lo que escribirías en cualquier módulo) ──
tracer = trace.get_tracer("lab03.dice", "1.0.0")
meter = metrics.get_meter("lab03.dice", "1.0.0")

roll_counter = meter.create_counter(
    "dice.rolls",
    unit="{roll}",
    description="Cantidad de lanzamientos por valor obtenido",
)

app = Flask(__name__)


@app.route("/rolldice")
def roll_dice():
    with tracer.start_as_current_span("rolldice") as span:
        value = roll()
        span.set_attribute("dice.roll.value", value)
        roll_counter.add(1, {"dice.roll.value": value})
        return str(value)


def roll():
    # Span hijo: hereda el trace_id del span actual ("rolldice").
    with tracer.start_as_current_span("roll") as span:
        span.add_event("lanzando el dado")
        value = randint(1, 6)
        span.set_attribute("dice.roll.value", value)
        return value
