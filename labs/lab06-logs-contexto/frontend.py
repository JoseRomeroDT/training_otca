"""Lab 6 · Servicio "dice-frontend" (puerto 8081): propagación MANUAL de contexto.

Sin librerías de instrumentación: el span SERVER y la propagación se hacen a mano
con la Propagators API (inject) para ver qué hacen por dentro las instrumentaciones.
  - W3C Trace Context → header "traceparent"
  - W3C Baggage       → header "baggage" (aquí: player.name)

Fuentes:
  https://opentelemetry.io/docs/languages/python/propagation/#manual-context-propagation
  https://opentelemetry.io/docs/concepts/context-propagation/
  https://opentelemetry.io/docs/concepts/signals/baggage/

Variables de entorno del lab:
  LAB_PROPAGAR   1 (por defecto) inyecta el contexto; 0 NO lo inyecta (rompe la traza a propósito)
  BACKEND_URL    por defecto http://localhost:8082/rolldice

Ejecutar: python frontend.py   (y luego: curl "localhost:8081/jugar?player=ana")
"""
import os

import requests
from flask import Flask, request

from opentelemetry import baggage, propagate
from opentelemetry.trace import SpanKind

from otel_setup import configurar_otel

PROPAGAR = os.getenv("LAB_PROPAGAR", "1") == "1"
BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:8082/rolldice")

tracer, logger = configurar_otel("dice-frontend")
app = Flask(__name__)


@app.route("/jugar")
def jugar():
    player = request.args.get("player", "anonimo")
    with tracer.start_as_current_span("GET /jugar", kind=SpanKind.SERVER) as span:
        span.set_attribute("player.name", player)

        # Contexto actual (con el span activo) + una entrada de baggage.
        ctx = baggage.set_baggage("player.name", player)
        headers = {}
        if PROPAGAR:
            propagate.inject(headers, context=ctx)  # escribe traceparent y baggage
        logger.info("frontend llama al backend para %s con headers=%s", player, headers)

        response = requests.get(BACKEND_URL, headers=headers, timeout=5)
        return {"frontend": "ok", "propagacion": PROPAGAR, "backend": response.json()}


if __name__ == "__main__":
    print(f"dice-frontend en http://localhost:8081 · propagación={'activada' if PROPAGAR else 'DESACTIVADA'}")
    app.run(host="0.0.0.0", port=8081)
