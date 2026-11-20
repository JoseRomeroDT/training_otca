"""Lab 6 · Servicio "dice-backend" (puerto 8082): extrae el contexto y correlaciona logs.

- propagate.extract() lee traceparent y baggage de los headers HTTP.
- El span SERVER se crea como hijo del contexto remoto (mismo trace_id).
- El baggage NO se convierte en atributo solo: hay que leerlo y agregarlo a mano.
- Los logs emitidos dentro del span llevan su trace_id y span_id (correlación).

Fuentes:
  https://opentelemetry.io/docs/languages/python/propagation/#manual-context-propagation
  https://opentelemetry.io/docs/concepts/signals/baggage/#baggage-is-not-the-same-as-attributes

Variables de entorno del lab:
  LAB_EXTRAER   1 (por defecto) extrae el contexto; 0 lo ignora (rompe la traza a propósito)

Ejecutar: python backend.py
"""
import os
import random

from flask import Flask, request

from opentelemetry import baggage, propagate, trace
from opentelemetry.trace import SpanKind

from otel_setup import configurar_otel

EXTRAER = os.getenv("LAB_EXTRAER", "1") == "1"

tracer, logger = configurar_otel("dice-backend")
app = Flask(__name__)


@app.route("/rolldice")
def rolldice():
    ctx = propagate.extract(request.headers) if EXTRAER else None
    player = baggage.get_baggage("player.name", ctx) if ctx is not None else None

    with tracer.start_as_current_span("GET /rolldice", context=ctx, kind=SpanKind.SERVER) as span:
        span.set_attribute("player.name", player or "desconocido")
        value = random.randint(1, 6)
        span.set_attribute("dice.roll.value", value)
        logger.info("backend: %s sacó %s", player or "desconocido", value)

        span_ctx = span.get_span_context()
        return {
            "valor": value,
            "jugador_desde_baggage": player,
            "trace_id": format(span_ctx.trace_id, "032x"),
            "traceparent_recibido": request.headers.get("traceparent"),
        }


if __name__ == "__main__":
    print(f"dice-backend en http://localhost:8082 · extracción={'activada' if EXTRAER else 'DESACTIVADA'}")
    app.run(host="0.0.0.0", port=8082)
