"""Lab 7 · App sin código de OpenTelemetry, configurada SOLO con variables OTEL_*.

Toda la configuración (servicio, exporters, protocolo, sampler, recursos…) viene
del entorno y la aplica el agente zero-code `opentelemetry-instrument`.

Fuentes:
  https://opentelemetry.io/docs/languages/sdk-configuration/
  https://opentelemetry.io/docs/zero-code/python/configuration/

Ejecutar: source otel.env && opentelemetry-instrument flask run -p 8080
"""
import logging
from random import randint

from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/rolldice")
def roll_dice():
    player = request.args.get("player", default="anonimo", type=str)
    result = randint(1, 6)
    logger.warning("%s is rolling the dice: %s", player, result)
    return str(result)


@app.route("/health")
def health():
    # Endpoint de salud: con OTEL_PYTHON_EXCLUDED_URLS=health no genera spans.
    return "ok"
