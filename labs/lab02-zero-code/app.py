"""Lab 2 · App base del "Getting Started" oficial de OpenTelemetry Python.

No contiene ni una línea de OpenTelemetry: la telemetría la agrega el agente
zero-code (`opentelemetry-instrument`) al ejecutarla.
Fuente: https://opentelemetry.io/docs/languages/python/getting-started/

Ejecutar sin instrumentar:   flask run -p 8080
Ejecutar instrumentada:      ver la guía del Laboratorio 2.
"""
import logging
from random import randint

from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@app.route("/rolldice")
def roll_dice():
    player = request.args.get("player", default=None, type=str)
    result = str(roll())
    if player:
        logger.warning("%s is rolling the dice: %s", player, result)
    else:
        logger.warning("Anonymous player is rolling the dice: %s", result)
    return result


def roll():
    return randint(1, 6)
