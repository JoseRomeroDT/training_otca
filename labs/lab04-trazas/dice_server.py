"""Lab 4 · Servicio "dice-server": trazas con processors, exporter OTLP y sampling.

- TracerProvider con Resource, sampler ParentBased(TraceIdRatioBased) y
  BatchSpanProcessor + OTLPSpanExporter (gRPC) hacia el Collector (localhost:4317).
- FlaskInstrumentor crea el span SERVER de cada request y EXTRAE el contexto
  W3C (traceparent) que envía el cliente.
- Spans manuales con atributos, eventos, estado de error y excepciones.

Fuentes:
  https://opentelemetry.io/docs/languages/python/instrumentation/#traces
  https://opentelemetry.io/docs/concepts/sampling/
  https://opentelemetry.io/docs/languages/python/exporters/

Variables de entorno del lab:
  LAB_SAMPLING_RATIO  proporción de trazas RAÍZ que se muestrean (0.0 a 1.0, por defecto 1.0)
  OTLP_ENDPOINT       destino OTLP gRPC (por defecto http://localhost:4317)

Ejecutar: python dice_server.py
"""
import os
import random
import time

from flask import Flask, request

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased
from opentelemetry.trace import Status, StatusCode

RATIO = float(os.getenv("LAB_SAMPLING_RATIO", "1.0"))
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")

resource = Resource.create({SERVICE_NAME: "dice-server", SERVICE_VERSION: "1.0.0"})
provider = TracerProvider(
    resource=resource,
    # Si llega un padre (traceparent), se respeta SU decisión; si no, se aplica el ratio.
    sampler=ParentBased(root=TraceIdRatioBased(RATIO)),
)
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)))
trace.set_tracer_provider(provider)

tracer = trace.get_tracer("lab04.dice_server", "1.0.0")

app = Flask(__name__)
FlaskInstrumentor().instrument_app(app)


@app.route("/rolldice")
def roll_dice():
    rolls = request.args.get("rolls", default=1, type=int)
    player = request.args.get("player", default="anonimo", type=str)

    # Span SERVER creado por la instrumentación de Flask: lo enriquecemos.
    server_span = trace.get_current_span()
    server_span.set_attribute("dice.rolls.requested", rolls)

    with tracer.start_as_current_span("validar-jugador", attributes={"player.name": player}) as span:
        if player == "tramposo":
            error = PermissionError("jugador bloqueado por trampa")
            span.record_exception(error)
            span.set_status(Status(StatusCode.ERROR, str(error)))
            return {"error": str(error)}, 403

    results = [roll(i) for i in range(max(1, min(rolls, 10)))]
    return {"player": player, "results": results}


def roll(index):
    with tracer.start_as_current_span("roll", attributes={"dice.roll.index": index}) as span:
        span.add_event("lanzando el dado")
        time.sleep(random.uniform(0.005, 0.03))
        value = random.randint(1, 6)
        span.set_attribute("dice.roll.value", value)
        if value == 6:
            span.add_event("¡seis!", {"dice.bonus": True})
        return value


if __name__ == "__main__":
    print(f"dice-server en http://localhost:8080 · sampling ratio raíz={RATIO} · OTLP={OTLP_ENDPOINT}")
    app.run(host="0.0.0.0", port=8080)
