---
title: "Laboratorio 6 · Logs correlacionados y propagación W3C"
description: "Dos servicios Python propagan a mano el contexto (W3C Trace Context y Baggage) con inject y extract, y sus logs viajan por OTLP correlacionados con la traza. Después rompes la propagación a propósito."
slug: "lab06-logs-contexto"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [lab, logs, contexto, propagacion, baggage]
duration: "50 minutos"
level: "intermediate"
objectives:
  - "Enviar logs del módulo logging de Python por OTLP con el logs bridge."
  - "Propagar el contexto a mano con inject (emisor) y extract (receptor)."
  - "Usar baggage y convertirlo explícitamente en atributo."
  - "Reconocer una traza rota por falta de propagación."
prerequisites:
  - "Laboratorio 5 completado."
  - "Entorno levantado (labs/lab-env/up.sh)."
links:
  - label: "Sesión 6: material de estudio"
    url: "../estudio/s06-logs-contexto.procedure.steps.md"
    icon: "book-open"
    highlight: true
  - label: "Código del laboratorio"
    url: "{{repo_url}}/tree/{{branch}}/labs/lab06-logs-contexto"
    icon: "github"
  - label: "Python · Propagation (oficial)"
    url: "https://opentelemetry.io/docs/languages/python/propagation/"
    icon: "external-link"
---

# {{ title }}

```text
curl ──▶ dice-frontend :8081 ──(traceparent + baggage)──▶ dice-backend :8082
          span GET /jugar                                 span GET /rolldice
          log "frontend llama…"                           log "backend: ana sacó N"
```

Aquí **no** hay librerías de instrumentación: la propagación es manual con `propagate.inject` y `propagate.extract`. Necesitas tres terminales.

:::step id="levantar" title="Levantar los dos servicios"
```bash
# Terminal 1
cd labs/lab06-logs-contexto && python backend.py
# Terminal 2
cd labs/lab06-logs-contexto && python frontend.py
# Terminal 3
curl -s "localhost:8081/jugar?player=ana" | python -m json.tool
```

- [ ] La respuesta incluye `"jugador_desde_baggage": "ana"` y un `traceparent_recibido`.
- [ ] En la terminal del frontend, el log muestra los headers inyectados: `traceparent` y `baggage: player.name=ana`.
:::

:::step id="traceparent" title="Leer el header traceparent"
El formato es `version-trace_id-parent_id-trace_flags` ([W3C Trace Context](https://www.w3.org/TR/trace-context/)), por ejemplo `00-2679fca0…3a50-baf88ae819190f07-03`:

- `00`: versión.
- 32 caracteres hexadecimales: el **Trace ID**.
- 16 caracteres: el **Span ID** del padre (el span `GET /jugar` del frontend).
- Las *trace flags*: el bit `01` indica **sampled**; el SDK también marca el bit `02` (**random**, de W3C Trace Context Level 2), por eso verás `03` ([Trace API · SpanContext](https://opentelemetry.io/docs/specs/otel/trace/api/#spancontext)).

- [ ] El `trace_id` que devuelve el backend es el mismo que va dentro del `traceparent`.
:::

:::step id="jaeger" title="La traza en Jaeger"
Abre Jaeger, elige el servicio `dice-frontend` y abre la traza `GET /jugar`.

- [ ] La traza tiene el span del frontend y, como hijo, `GET /rolldice` del backend.
- [ ] El span del backend tiene el atributo `player.name = ana`: el backend lo **leyó del baggage y lo agregó a mano** (el baggage no es un atributo por sí solo).
:::

:::step id="logs" title="Logs correlacionados"
Los logs llegan al Collector, que los muestra con el exporter `debug` en modo `detailed`:

```bash
docker logs otel-collector 2>&1 | grep -A12 "sacó"
```

- [ ] El log del backend tiene `SeverityText: INFO`, el `Body` del mensaje y un `Trace ID` igual al de la traza en Jaeger.
- [ ] Su `Span ID` es el del span `GET /rolldice` del backend.
- [ ] El log del frontend tiene el mismo `Trace ID` y el `Span ID` de `GET /jugar`.
:::

:::step id="romper" title="Romper la propagación a propósito"
:::substep id="sin-inject" title="El emisor no inyecta"
Detén el frontend y reinícialo con `LAB_PROPAGAR=0 python frontend.py`. Repite el `curl`.

- [ ] `traceparent_recibido` es `null` y `jugador_desde_baggage` es `null`.
- [ ] En Jaeger ahora hay **dos trazas separadas** (una por servicio) para una misma solicitud.
- [ ] Los logs de frontend y backend tienen Trace ID **distintos**: ya no se pueden correlacionar.
:::

:::substep id="sin-extract" title="El receptor no extrae"
Reinicia el frontend normal (`python frontend.py`) y el backend con `LAB_EXTRAER=0 python backend.py`.

- [ ] Ahora `traceparent_recibido` **sí** llega, pero la traza igual se parte: el header viajó y nadie lo leyó.
- [ ] Restauré ambos servicios sin variables y los detuve con `Ctrl+C`.
:::
:::
