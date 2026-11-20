"""Lab 4 · Servicio "dice-player": cliente que juega partidas contra dice-server.

Cada partida es una traza:
  jugar-partida (INTERNAL, dice-player)
    └─ GET (CLIENT, creado por RequestsInstrumentor; inyecta el header traceparent)
         └─ GET /rolldice (SERVER, dice-server) → validar-jugador, roll, roll…

Variables de entorno del lab:
  LAB_SAMPLING_RATIO  proporción de partidas (trazas raíz) que se muestrean (por defecto 1.0)
  LAB_PARTIDAS        cuántas partidas jugar (por defecto 10)
  LAB_JUGADOR         nombre del jugador (por defecto: aleatorio; "tramposo" provoca un error)
  DICE_SERVER_URL     por defecto http://localhost:8080
  OTLP_ENDPOINT       destino OTLP gRPC (por defecto http://localhost:4317)

Ejecutar: python player.py
"""
import os
import random
import time

import requests

from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.instrumentation.requests import RequestsInstrumentor
from opentelemetry.sdk.resources import SERVICE_NAME, SERVICE_VERSION, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.sdk.trace.sampling import ParentBased, TraceIdRatioBased

RATIO = float(os.getenv("LAB_SAMPLING_RATIO", "1.0"))
PARTIDAS = int(os.getenv("LAB_PARTIDAS", "10"))
JUGADOR = os.getenv("LAB_JUGADOR", "")
SERVER = os.getenv("DICE_SERVER_URL", "http://localhost:8080")
OTLP_ENDPOINT = os.getenv("OTLP_ENDPOINT", "http://localhost:4317")

resource = Resource.create({SERVICE_NAME: "dice-player", SERVICE_VERSION: "1.0.0"})
provider = TracerProvider(resource=resource, sampler=ParentBased(root=TraceIdRatioBased(RATIO)))
provider.add_span_processor(BatchSpanProcessor(OTLPSpanExporter(endpoint=OTLP_ENDPOINT, insecure=True)))
trace.set_tracer_provider(provider)

RequestsInstrumentor().instrument()
tracer = trace.get_tracer("lab04.player", "1.0.0")


def jugar(numero):
    jugador = JUGADOR or random.choice(["ana", "luis", "sofia", "mateo"])
    with tracer.start_as_current_span("jugar-partida") as span:
        span.set_attribute("player.name", jugador)
        span.set_attribute("game.number", numero)
        rolls = random.randint(1, 3)
        response = requests.get(f"{SERVER}/rolldice", params={"rolls": rolls, "player": jugador}, timeout=5)
        sampled = span.get_span_context().trace_flags.sampled
        trace_id = format(span.get_span_context().trace_id, "032x")
        print(f"partida {numero:>2} · {jugador:<8} · HTTP {response.status_code} · "
              f"trace_id={trace_id} · muestreada={sampled}")


if __name__ == "__main__":
    print(f"dice-player → {SERVER} · {PARTIDAS} partidas · sampling ratio raíz={RATIO}")
    for n in range(1, PARTIDAS + 1):
        jugar(n)
        time.sleep(0.3)
    # Vacía el BatchSpanProcessor antes de salir (si no, se pierden los últimos spans).
    provider.shutdown()
