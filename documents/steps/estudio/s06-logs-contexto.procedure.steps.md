---
title: "Sesión 6 · Logs, contexto y propagación"
description: "Logs en OpenTelemetry (bridge y modelo de datos), la Context API, la Propagators API con W3C Trace Context y W3C Baggage, y la correlación de logs con trazas. Dominio 2 (46 %)."
slug: "s06-logs-contexto"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-2, logs, contexto, propagacion, baggage]
duration: "2 horas"
level: "intermediate"
objectives:
  - "Usar el logs bridge del SDK con la librería de logging del lenguaje."
  - "Usar la Context API para leer y activar contexto."
  - "Aplicar W3C Trace Context y W3C Baggage con la Propagators API (inject/extract)."
  - "Correlacionar logs con trazas mediante el Trace ID y el Span ID."
links:
  - label: "Laboratorio 6: logs y contexto"
    url: "../labs/lab06-logs-contexto.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Context propagation (concepto)"
    url: "https://opentelemetry.io/docs/concepts/context-propagation/"
    icon: "book-open"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 2 · The OpenTelemetry API and SDK (46 %)** — competencias *Signals (Log)* y *Context Propagation*. La propagación vuelve en el Dominio 4, ahora desde el punto de vista de la depuración.

:::step id="logs" title="Logs en OpenTelemetry"
De [Logs](https://opentelemetry.io/docs/concepts/signals/logs/) ([español](https://opentelemetry.io/es/docs/concepts/signals/logs/)):

- OpenTelemetry está pensado para trabajar con **los logs que ya produces**: los correlaciona con otras señales, les agrega contexto y los normaliza.
- Como desarrollador **no llamas a la Logs Bridge API**: usas tu librería de logging de siempre con un **appender o bridge** que envía los registros al SDK. La Bridge API es para autores de librerías de logging.
- Al activar un SDK o la auto-instrumentación, los logs se **correlacionan automáticamente** con la traza y el span activos.
- Los logs son una señal **estable** en la especificación. Formas: **estructurados** (esquema estable; recomendados en producción), **no estructurados** y **semiestructurados** (clave=valor o JSON sin esquema estable).
- En el **Collector**: receivers para fuentes conocidas, el receiver `filelog` (en versiones recientes `file_log`) para leer archivos, y processors como `transform` para parsear y normalizar.
- **Events** son un tipo especial de log: todo event es un log, no todo log es un event.

En Python el bridge es un `LoggingHandler` que se agrega al módulo estándar `logging` ([Python · Logs](https://opentelemetry.io/docs/languages/python/instrumentation/#logs)). Con el agente zero-code, desde Python 1.40.0 la auto-instrumentación de logs viene **activada por defecto** (`OTEL_PYTHON_LOG_AUTO_INSTRUMENTATION`) ([configuración del agente](https://opentelemetry.io/docs/zero-code/python/configuration/#logging)).

**Campos de un log record**: Timestamp, ObservedTimestamp, **TraceId**, **SpanId**, TraceFlags, SeverityText, SeverityNumber, Body, Resource, InstrumentationScope, Attributes y EventName ([Log Record](https://opentelemetry.io/docs/concepts/signals/logs/#log-record)).

- [ ] Sé qué es un logs bridge y qué campos permiten la correlación con trazas.
:::

:::step id="contexto" title="Contexto y Context API"
De [Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) ([español](https://opentelemetry.io/es/docs/concepts/context-propagation/)) y la [especificación de Context](https://opentelemetry.io/docs/specs/otel/context/):

- El **contexto** es un objeto con la información que permite **correlacionar** una señal con otra entre quien envía y quien recibe (p. ej., el Trace ID y el Span ID del servicio A que el servicio B usa como padre).
- Un `Context` es **inmutable**: sus operaciones de escritura devuelven un contexto nuevo.
- La Context API permite **activar** un contexto como actual (*attach*) y restaurar el anterior (*detach*).

```python
from opentelemetry import baggage, context

ctx = baggage.set_baggage("player.name", "ana")   # devuelve un Context NUEVO
token = context.attach(ctx)                         # lo hace actual
try:
    ...                                             # aquí baggage.get_baggage("player.name") == "ana"
finally:
    context.detach(token)                           # vuelve al contexto anterior
```
:::

:::step id="propagacion" title="Propagación: inject y extract"
- **Propagación** es el mecanismo que mueve el contexto entre servicios y procesos: lo **serializa** en el emisor y lo **deserializa** en el receptor. Normalmente lo hacen las **librerías de instrumentación**; a mano se usa la [Propagators API](https://opentelemetry.io/docs/specs/otel/context/api-propagators/).
- Emisor: **inject** del contexto en el *carrier* (p. ej., los headers HTTP). Receptor: **extract** del carrier y uso del contexto extraído como padre.
- El propagador por defecto usa **W3C Trace Context** (header `traceparent` con el formato `version-trace_id-parent_id-trace_flags`, y `tracestate`). En Python el valor por defecto equivale a `OTEL_PROPAGATORS="tracecontext,baggage"`; otros valores: `b3`, `b3multi`, `jaeger`, `xray`, `ottrace`, `none` ([Python · propagación](https://opentelemetry.io/docs/languages/python/instrumentation/#change-the-default-propagation-format)).
- Las variables de entorno **tienen prioridad** sobre lo configurado en código.

```python
from opentelemetry import propagate
headers = {}
propagate.inject(headers)                 # emisor: escribe traceparent (y baggage)
ctx = propagate.extract(request.headers)  # receptor: lee los headers
with tracer.start_as_current_span("GET /rolldice", context=ctx): ...
```

Fuente: [Python · Propagation](https://opentelemetry.io/docs/languages/python/propagation/).

- [ ] Sé qué hace inject, qué hace extract y qué viaja en `traceparent`.
:::

:::step id="baggage" title="Baggage"
De [Baggage](https://opentelemetry.io/docs/concepts/signals/baggage/) ([español](https://opentelemetry.io/es/docs/concepts/signals/baggage/)):

- Es un almacén **clave-valor** que vive junto al contexto y se **propaga** entre servicios (header W3C `baggage`).
- Sirve para llevar aguas abajo datos que solo existen al inicio de la solicitud: IDs de cuenta o de usuario, IDs de producto, IP de origen.
- **No es lo mismo que los atributos**: para que un valor de baggage aparezca en un span, métrica o log hay que **leerlo y agregarlo explícitamente** (algunos lenguajes tienen *Baggage Span Processors* que lo hacen).
- **Seguridad**: viaja en headers HTTP visibles, la instrumentación automática lo incluye en casi todas las llamadas salientes (puede llegar a terceros) y no tiene verificación de integridad. No pongas datos sensibles (credenciales, API keys, datos personales).

- [ ] Sé para qué sirve el baggage y por qué no es un atributo.
:::

:::step id="seguridad" title="Propagación y seguridad"
Buenas prácticas de [Context propagation · Security](https://opentelemetry.io/docs/concepts/context-propagation/#security-best-practices):

- **Contexto entrante** de servicios externos: puede venir falsificado; considera ignorarlo o sanearlo.
- **Contexto saliente** hacia servicios externos: los IDs y el baggage pueden revelar información interna; considera no propagar hacia endpoints públicos.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Logs](https://opentelemetry.io/docs/concepts/signals/logs/) · [español](https://opentelemetry.io/es/docs/concepts/signals/logs/)
- [ ] [Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) · [español](https://opentelemetry.io/es/docs/concepts/context-propagation/)
- [ ] [Baggage](https://opentelemetry.io/docs/concepts/signals/baggage/) · [español](https://opentelemetry.io/es/docs/concepts/signals/baggage/)
- [ ] [Python · Logs](https://opentelemetry.io/docs/languages/python/instrumentation/#logs) y [Python · Propagation](https://opentelemetry.io/docs/languages/python/propagation/)
- [ ] [W3C Trace Context](https://www.w3.org/TR/trace-context/) (especificación del header `traceparent`)
- [ ] Repositorio [opentelemetry-python-contrib](https://github.com/open-telemetry/opentelemetry-python-contrib)
:::

:::step id="repaso" title="Puntos clave para repasar"
- El desarrollador usa su librería de logging + un **bridge**; la Logs Bridge API es para autores de librerías.
- La correlación log ↔ traza se hace con **TraceId** y **SpanId** en el log record.
- Propagadores por defecto: **tracecontext** y **baggage**.
- Emisor → **inject**; receptor → **extract**.
- `traceparent` = `version-trace_id-parent_id-trace_flags`.
- Baggage ≠ atributos, y no lleva datos sensibles.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 6](../labs/lab06-logs-contexto.labguide.steps.md).
:::
