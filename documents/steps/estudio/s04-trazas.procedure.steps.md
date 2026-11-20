---
title: "Sesión 4 · Trazas: spans, processors y sampling"
description: "Anatomía de un span (contexto, atributos, eventos, links, estado y kind), span processors y exporters, head y tail sampling, samplers del SDK y propagación de contexto entre spans. Dominio 2 (46 %)."
slug: "s04-trazas"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-2, trazas, spans, sampling]
level: "intermediate"
objectives:
  - "Configurar un TracerProvider con span processors y exporters."
  - "Crear spans con atributos, eventos, links y estado."
  - "Aplicar estrategias de head sampling y distinguirlas del tail sampling."
  - "Propagar el contexto entre spans, dentro de un proceso y entre servicios."
links:
  - label: "Laboratorio 4: trazas distribuidas"
    url: "../labs/lab04-trazas.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Traces (concepto)"
    url: "https://opentelemetry.io/docs/concepts/signals/traces/"
    icon: "book-open"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 2 · The OpenTelemetry API and SDK (46 %)** — competencias *Signals (Tracing)* y *SDK Pipelines*.

:::step id="span" title="Anatomía de un span"
De [Traces](https://opentelemetry.io/docs/concepts/signals/traces/) ([español](https://opentelemetry.io/es/docs/concepts/signals/traces/)):

- **Span Context** (inmutable): Trace ID, Span ID, **Trace Flags** (p. ej. *sampled*) y **Trace State** (pares clave-valor específicos de cada sistema de trazas). Es la parte del span que se **propaga**.
- **Atributos**: pares clave-valor. Conviene agregarlos **al crear el span**, porque así están disponibles para el *sampling* del SDK.
- **Eventos**: un mensaje estructurado en un **momento puntual** del span. Regla oficial: si el *timestamp* importa, usa un evento; si no, un atributo.
- **Links**: asocian un span con otros spans con relación causal, típico en trabajo **asíncrono** (p. ej., una operación encolada que se procesa después en otra traza).
- **Estado**: `Unset` (por defecto; terminó sin error), `Error` u `Ok`. `Ok` solo se pone cuando el desarrollador quiere marcarlo **explícitamente** como exitoso; normalmente no hace falta.
- **Kind**: `Client`, `Server`, `Internal` (por defecto), `Producer` o `Consumer`. El padre de un span `Server` suele ser un `Client` remoto; el padre de un `Consumer` es siempre un `Producer`.

- [ ] Sé cuándo usar atributo, evento o link, y qué significa cada estado y kind.
:::

:::step id="python" title="Spans en Python"
De [Python · Traces](https://opentelemetry.io/docs/languages/python/instrumentation/#traces):

```python
with tracer.start_as_current_span("padre") as padre:      # pasa a ser el span actual
    with tracer.start_as_current_span("hijo") as hijo:     # hijo del span actual (mismo trace_id)
        hijo.set_attribute("dice.roll.value", 6)
        hijo.add_event("¡seis!")

span = trace.get_current_span()                             # enriquecer el span actual
try:
    ...
except Exception as ex:
    span.set_status(Status(StatusCode.ERROR))
    span.record_exception(ex)
```

- `start_as_current_span` crea el span **y** lo hace actual; `start_span` lo crea **sin** hacerlo actual (útil para operaciones concurrentes o asíncronas).
- También existe el decorador `@tracer.start_as_current_span("nombre")`.
- Para un link: `trace.Link(span_context)` al crear el span.
:::

:::step id="processors" title="Span processors y exporters"
El pipeline del SDK de trazas es: **Tracer → Span processor → Span exporter**.

- **Simple processor**: entrega cada span al exporter en cuanto termina.
- **Batch processor**: agrupa spans y los exporta en lotes ([Trace SDK](https://opentelemetry.io/docs/specs/otel/trace/sdk/#built-in-span-processors)). Valores por defecto ([variables de entorno del SDK](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#batch-span-processor)):

| Variable | Significado | Por defecto |
|---|---|---|
| `OTEL_BSP_SCHEDULE_DELAY` | ms entre dos exportaciones | 5000 |
| `OTEL_BSP_EXPORT_TIMEOUT` | ms máximos por exportación | 30000 |
| `OTEL_BSP_MAX_QUEUE_SIZE` | tamaño máximo de la cola | 2048 |
| `OTEL_BSP_MAX_EXPORT_BATCH_SIZE` | spans por lote (≤ tamaño de cola) | 512 |

- Exporters: consola (para depurar) u **OTLP** (gRPC o HTTP/protobuf) hacia el Collector o un backend ([Python · Exporters](https://opentelemetry.io/docs/languages/python/exporters/)).
- Antes de terminar el proceso hay que llamar a `shutdown()` (o `force_flush()`) para no perder lo que queda en el lote.

- [ ] Sé la diferencia entre simple y batch y por qué existe `shutdown()`.
:::

:::step id="sampling" title="Sampling: head y tail"
De [Sampling](https://opentelemetry.io/docs/concepts/sampling/) ([español](https://opentelemetry.io/es/docs/concepts/sampling/)):

- Terminología: una traza **sampled** (muestreada) se procesa y exporta; una **not sampled** no. Decir "muestrear fuera" datos es incorrecto.
- Sirve para **reducir costos sin perder visibilidad**, porque una muestra es **representativa**.
- Considéralo si generas **1000 o más trazas por segundo**, si la mayoría es tráfico sano o si tienes criterios claros (errores, latencia). Evítalo si generas muy poco, si solo usas datos agregados o si una regulación impide descartar datos.
- **Head sampling**: decide **lo antes posible**, sin ver la traza completa. Lo más común es el muestreo **probabilístico consistente** basado en el **Trace ID**: se muestrean trazas completas. Fácil, eficiente y aplicable en cualquier punto, pero **no** garantiza quedarse con todas las trazas con error.
- **Tail sampling**: decide mirando **todos o casi todos los spans** de la traza (p. ej., quedarse siempre con las que tienen error o mucha latencia). Más potente, pero más difícil de implementar y operar (es *stateful*). En el Collector: `probabilistic_sampler` y `tail_sampling`.
- Se pueden **combinar**: head sampling en el origen y tail sampling después.

- [ ] Puedo explicar cuándo conviene head, tail o ambos.
:::

:::step id="samplers" title="Samplers del SDK"
Del [Trace SDK](https://opentelemetry.io/docs/specs/otel/trace/sdk/#built-in-samplers):

- **AlwaysOn**, **AlwaysOff**, **TraceIdRatioBased** y **ParentBased**. El sampler **por defecto** es `ParentBased(root=AlwaysOn)`.
- **ParentBased** es un decorador: si el span no tiene padre usa el sampler `root`; si tiene padre, **respeta la decisión del padre** (por defecto: padre muestreado → AlwaysOn; no muestreado → AlwaysOff), sea remoto o local.
- `TraceIdRatioBased` ignora la decisión del padre; para respetarla se usa **dentro** de `ParentBased`.
- Por variables de entorno ([SDK env vars](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#general-sdk-configuration)): `OTEL_TRACES_SAMPLER` = `always_on`, `always_off`, `traceidratio`, `parentbased_always_on` (por defecto), `parentbased_always_off`, `parentbased_traceidratio`…; y `OTEL_TRACES_SAMPLER_ARG` con la probabilidad entre 0 y 1 (por defecto 1.0).

> [!NOTE]
> En la especificación actual, `TraceIdRatioBased` sigue siendo estable pero está **marcado para ser reemplazado** por el `ProbabilitySampler` (en desarrollo); los SDK no lo modificarán antes del 1 de enero de 2027. El examen y la mayoría de la documentación siguen usando `traceidratio`.

- [ ] Puedo predecir qué pasa con un servicio con `ParentBased` cuando el cliente muestrea el 50 %.
:::

:::step id="contexto" title="Propagar el contexto entre spans"
- **Dentro del proceso**: el span "actual" vive en el **Context**; los spans nuevos lo toman como padre automáticamente.
- **Entre servicios**: el contexto se **inyecta** en el mensaje saliente y se **extrae** en el servicio que lo recibe. Por defecto se usa el header `traceparent` de **W3C Trace Context**, con el formato `version-trace_id-parent_id-trace_flags` ([Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/), [español](https://opentelemetry.io/es/docs/concepts/context-propagation/)).
- Normalmente lo hacen las **librerías de instrumentación** (en el laboratorio: `requests` inyecta y `Flask` extrae). Lo harás a mano en la Sesión 6.
- Las *trace flags* reconocidas hoy son **Sampled** y **Random** ([Trace API](https://opentelemetry.io/docs/specs/otel/trace/api/#spancontext)).

- [ ] Sé cómo viaja una traza de un servicio a otro.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Traces](https://opentelemetry.io/docs/concepts/signals/traces/) · [español](https://opentelemetry.io/es/docs/concepts/signals/traces/)
- [ ] [Sampling](https://opentelemetry.io/docs/concepts/sampling/) · [español](https://opentelemetry.io/es/docs/concepts/sampling/)
- [ ] [Python · Traces](https://opentelemetry.io/docs/languages/python/instrumentation/#traces)
- [ ] [Trace SDK: samplers y processors (especificación)](https://opentelemetry.io/docs/specs/otel/trace/sdk/)
- [ ] [Ejemplos de opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python/tree/main/docs/examples)
:::

:::step id="repaso" title="Puntos clave para repasar"
- Span Context = Trace ID + Span ID + Trace Flags + Trace State; es lo que se propaga.
- Estado por defecto **Unset**; `Ok` solo si se marca explícitamente.
- Kind por defecto **Internal**.
- Batch processor por defecto: **5000 ms**, cola **2048**, lote **512**, timeout **30000 ms**.
- Sampler por defecto: **ParentBased(root=AlwaysOn)**.
- Head = decisión temprana con el Trace ID; tail = decisión con la traza completa.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 4](../labs/lab04-trazas.labguide.steps.md).
:::
