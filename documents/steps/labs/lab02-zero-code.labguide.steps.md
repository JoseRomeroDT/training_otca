---
title: "Laboratorio 2 · Instrumentación zero-code en Python"
description: "Instrumenta sin cambiar código una app Flask con el agente de Python, mira las tres señales en la consola, compara las convenciones semánticas antiguas y estables, y envía todo al Collector."
slug: "lab02-zero-code"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [lab, zero-code, python, semantic-conventions]
duration: "45 minutos"
level: "beginner"
objectives:
  - "Instrumentar una app Flask con opentelemetry-bootstrap y opentelemetry-instrument."
  - "Reconocer en la salida un span SERVER, un log correlacionado y métricas HTTP."
  - "Comparar las convenciones semánticas HTTP antiguas y estables."
  - "Enviar la telemetría al Collector por OTLP y verla en Jaeger."
prerequisites:
  - "Laboratorio 0 completado y entorno levantado (labs/lab-env/up.sh)."
links:
  - label: "Sesión 2: material de estudio"
    url: "../estudio/s02-instrumentacion-semconv.procedure.steps.md"
    icon: "book-open"
    highlight: true
  - label: "Código del laboratorio"
    url: "{{repo_url}}/tree/{{branch}}/labs/lab02-zero-code"
    icon: "github"
  - label: "Getting Started de Python (oficial)"
    url: "https://opentelemetry.io/docs/languages/python/getting-started/"
    icon: "external-link"
---

# {{ title }}

Seguimos el [Getting Started oficial de Python](https://opentelemetry.io/docs/languages/python/getting-started/). Necesitas **dos terminales**: una para la app (déjala corriendo) y otra para enviarle solicitudes.

:::step id="app" title="La app sin instrumentar"
```bash
cd labs/lab02-zero-code
cat app.py
flask run -p 8080
```

En la otra terminal:

```bash
curl "localhost:8080/rolldice?player=ana"
```

- [ ] La app responde un número del 1 al 6 y `app.py` no tiene código de OpenTelemetry.
- [ ] Detuve la app con `Ctrl+C`.
:::

:::step id="bootstrap" title="Instalar el agente"
El Codespace ya trae `opentelemetry-distro` y `opentelemetry-exporter-otlp`. Mira qué instrumentaciones recomienda el agente para los paquetes instalados y luego instálalas:

```bash
opentelemetry-bootstrap            # lista las recomendadas
opentelemetry-bootstrap -a install # las instala
```

- [ ] En la lista aparece `opentelemetry-instrumentation-flask`.
:::

:::step id="consola" title="Ejecutar instrumentado con salida a la consola"
```bash
opentelemetry-instrument \
    --traces_exporter console \
    --metrics_exporter console \
    --logs_exporter console \
    --service_name dice-server \
    flask run -p 8080
```

Envía varias solicitudes desde la otra terminal (`curl "localhost:8080/rolldice?player=ana"`). Las métricas se exportan cada 60 s por defecto: espera un minuto o detén la app con `Ctrl+C` para forzar la última exportación.

- [ ] Veo un span `GET /rolldice` con `"kind": "SpanKind.SERVER"` y `"parent_id": null` (root span).
- [ ] Veo un log `ana is rolling the dice: …` cuyo `trace_id` y `span_id` coinciden con los del span.
- [ ] Veo métricas de la instrumentación de Flask (`http.server.active_requests` y `http.server.duration`).
- [ ] En `resource` aparecen `service.name: dice-server`, `telemetry.sdk.*` y `telemetry.auto.version`.
:::

:::step id="semconv" title="Convenciones semánticas: antiguas y estables"
Mira los atributos del span anterior: `http.method`, `http.status_code`, `http.target`… Son los nombres **experimentales anteriores**, que las instrumentaciones de Python siguen emitiendo por defecto. Ahora activa los **estables** ([semantic convention stability](https://opentelemetry.io/docs/languages/python/instrumentation/#semantic-convention-stability)):

```bash
OTEL_SEMCONV_STABILITY_OPT_IN=http opentelemetry-instrument \
    --traces_exporter console --metrics_exporter console --logs_exporter console \
    --service_name dice-server flask run -p 8080
```

| Antes (por defecto) | Con `OTEL_SEMCONV_STABILITY_OPT_IN=http` |
|---|---|
| `http.method` | `http.request.method` |
| `http.status_code` | `http.response.status_code` |
| `http.target` | `url.path` + `url.query` |
| `net.peer.ip` | `client.address` |
| métrica `http.server.duration` (ms) | métrica `http.server.request.duration` (s) |

- [ ] Vi los atributos estables en el span y la métrica `http.server.request.duration`.
- [ ] Sé que `http/dup` emite ambas versiones durante una migración.
:::

:::step id="otlp" title="Enviar al Collector y ver la traza en Jaeger"
Cambia los exporters de la consola a OTLP (por defecto, gRPC):

```bash
opentelemetry-instrument \
    --traces_exporter otlp --metrics_exporter otlp --logs_exporter otlp \
    --service_name dice-server \
    --exporter_otlp_endpoint http://localhost:4317 \
    flask run -p 8080
```

Envía varias solicitudes y abre Jaeger (puerto 16686).

- [ ] En Jaeger aparece el servicio `dice-server` con trazas `GET /rolldice`.
- [ ] `docker logs otel-collector 2>&1 | grep -A3 "is rolling the dice"` muestra los logs que llegaron al Collector.
:::

:::step id="manual" title="(Opcional) Sumar un span manual a la instrumentación automática"
La instrumentación automática ve los "bordes" (la request HTTP), no tu lógica. Agrega un span propio como en la [guía oficial](https://opentelemetry.io/docs/languages/python/getting-started/#add-manual-instrumentation-to-automatic-instrumentation): en `app.py`, importa la API y envuelve `roll()`:

```python
from opentelemetry import trace

tracer = trace.get_tracer("diceroller.tracer")

def roll():
    # Crea un span hijo del span actual (el de la request)
    with tracer.start_as_current_span("roll") as rollspan:
        res = randint(1, 6)
        rollspan.set_attribute("roll.value", res)
        return res
```

Vuelve a ejecutar con la salida a consola o a OTLP.

- [ ] El span `roll` tiene como `parent_id` el `span_id` de `GET /rolldice`.
- [ ] Deshice el cambio con `git checkout labs/lab02-zero-code/app.py`.
:::
