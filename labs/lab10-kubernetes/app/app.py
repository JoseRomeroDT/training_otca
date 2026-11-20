"""Lab 10 · App de dados para Kubernetes, SIN código de OpenTelemetry.

El OpenTelemetry Operator inyecta la auto-instrumentación de Python en el pod
(init container + PYTHONPATH + variables OTEL_*) gracias a la anotación
instrumentation.opentelemetry.io/inject-python: "true".
Fuente: https://opentelemetry.io/docs/platforms/kubernetes/operator/automatic/
"""
import logging
from random import randint

from flask import Flask, request

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("dice-k8s")


@app.route("/rolldice")
def roll_dice():
    player = request.args.get("player", default="anonimo", type=str)
    result = randint(1, 6)
    logger.warning("%s is rolling the dice: %s", player, result)
    return str(result)


@app.route("/health")
def health():
    return "ok"


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
