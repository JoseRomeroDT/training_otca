"""Lab 5 · "dice-server" con métricas de negocio exportadas por OTLP.

- MeterProvider + PeriodicExportingMetricReader + OTLPMetricExporter (gRPC) → Collector → Prometheus.
- Un instrumento de cada tipo útil para el examen:
    Counter, UpDownCounter, Histogram, Gauge (síncronos) y ObservableGauge (asíncrono).
- Una View que cambia la agregación del histograma (límites de buckets en segundos).

Fuentes:
  https://opentelemetry.io/docs/concepts/signals/metrics/
  https://opentelemetry.io/docs/languages/python/instrumentation/#metrics
  https://opentelemetry.io/docs/specs/otel/metrics/sdk/

Variables de entorno del lab:
  LAB_USAR_VIEW      1 (por defecto) aplica la View de buckets; 0 usa los buckets por defecto
  OTLP_ENDPOINT      destino OTLP gRPC (por defecto http://localhost:4317)

Ejecutar: python dice_server.py   (y genera tráfico con ../lab04-trazas/player.py)
"""
import os
import random
import time

from flask import Flask, request

from opentelemetry import metrics, trace
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.metrics import CallbackOptions, Observation
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader
from opentelemetry.sdk.metrics.view import ExplicitBucketHistogramAggregation, View
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")
USAR_VIEW = os.getenv("LAB_USAR_VIEW", "1") == "1"

resource = Resource.create({SERVICE_NAME: "dice-server", SERVICE_VERSION: "1.1.0"})

# ── Trazas (igual que en el Lab 4) ──────────────────────────────────────────
tracer_provider = TracerProvider(resource=resource)
tracer_provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)))
trace.set_tracer_provider(tracer_provider)
tracer = trace.get_tracer("lab05.dice_server", "1.1.0")

# ── Métricas ────────────────────────────────────────────────────────────────
views = []
if USAR_VIEW:
    # Los buckets por defecto (0, 5, 10, 25 … 10000) están pensados para milisegundos.
    # Como medimos en segundos, una View define límites adecuados para este histograma.
    views.append(
        View(
            instrument_name="dice.roll.duration",
            aggregation=ExplicitBucketHistogramAggregation(boundaries=[0.005, 0.01, 0.02, 0.03, 0.05, 0.1]),
        )
    )

reader = PeriodicExportingMetricReader(
    OTLPMetricExporter(endpoint=OTLP_ENDPOINT, insecure=True),
    export_interval_millis=5_000,  # por defecto 60000 ms; 5 s para ver resultados rápido
)
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader], views=views))
meter = metrics.get_meter("lab05.dice_server", "1.1.0")

# Counter: solo sube (monotónico) → lanzamientos por valor.
rolls_counter = meter.create_counter("dice.rolls", unit="{roll}", description="Lanzamientos por valor")
# UpDownCounter: sube y baja → requests en curso.
active_requests = meter.create_up_down_counter(
    "dice.requests.active", unit="{request}", description="Requests de /rolldice en curso"
)
# Histogram: distribución de valores → duración de cada lanzamiento.
roll_duration = meter.create_histogram("dice.roll.duration", unit="s", description="Duración de cada lanzamiento")
# Gauge síncrono: último valor medido.
last_roll = meter.create_gauge("dice.roll.last", description="Último valor obtenido")

# ObservableGauge (asíncrono): el SDK llama al callback en cada recolección.
jugadores_vistos = set()


def observar_jugadores(options: CallbackOptions):
    yield Observation(len(jugadores_vistos))


meter.create_observable_gauge(
    "dice.players.known",
    callbacks=[observar_jugadores],
    unit="{player}",
    description="Jugadores distintos vistos desde el arranque",
)

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


@app.route("/rolldice")
def roll_dice():
    rolls = max(1, min(request.args.get("rolls", default=1, type=int), 10))
    player = request.args.get("player", default="anonimo", type=str)
    jugadores_vistos.add(player)
    active_requests.add(1)
    try:
        results = [roll() for _ in range(rolls)]
        return {"player": player, "results": results}
    finally:
        active_requests.add(-1)


def roll():
    with tracer.start_as_current_span("roll") as span:
        start = time.perf_counter()
        time.sleep(random.uniform(0.005, 0.03))
        value = random.randint(1, 6)
        span.set_attribute("dice.roll.value", value)
        attrs = {"dice.roll.value": value}
        rolls_counter.add(1, attrs)
        roll_duration.record(time.perf_counter() - start)
        last_roll.set(value)
        return value


if __name__ == "__main__":
    print(f"dice-server (métricas) en http://localhost:8080 · View de buckets={'sí' if USAR_VIEW else 'no'}")
    app.run(host="0.0.0.0", port=8080)
