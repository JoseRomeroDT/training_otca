---
title: "Sesión 11 · Mantenimiento y depuración de pipelines"
description: "Diagnóstico de fallas de propagación de contexto, herramientas de depuración del Collector (debug exporter, zPages, telemetría interna), manejo de errores y resiliencia, y gestión de telemetry schemas. Dominio 4 (10 %)."
slug: "s11-depuracion"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-4, depuracion, troubleshooting, schemas, resiliencia]
duration: "2 horas"
level: "advanced"
objectives:
  - "Diagnosticar fallas de propagación de contexto."
  - "Usar el debug exporter, zPages y las métricas internas del Collector."
  - "Aplicar el manejo de errores de OpenTelemetry y la resiliencia del Collector (colas y reintentos)."
  - "Entender qué son los telemetry schemas y cómo ayudan a migrar convenciones."
links:
  - label: "Laboratorio 11: depuración"
    url: "../labs/lab11-depuracion.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Quiz del Dominio 4"
    url: "../../tests/quiz-d4-depuracion.test.md"
    icon: "graduation-cap"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 4 · Maintaining and Debugging Observability Pipelines (10 %)** — competencias *Context Propagation*, *Debugging Pipelines*, *Error Handling* y *Schema Management*.

:::step id="propagacion" title="Fallas de propagación de contexto"
La propagación funciona con **inject** en quien llama y **extract** en quien recibe, usando el mismo formato de propagación ([Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/)). Si algo de eso falta, la traza se parte. Síntomas y causas que verás en el laboratorio:

| Síntoma | Causa probable | Cómo confirmarlo |
|---|---|---|
| Una solicitud aparece como **dos o más trazas** en Jaeger | El emisor no inyecta (`traceparent` ausente) o el receptor no extrae | Revisar los headers que llegan; en el lab, `traceparent_recibido` es `null` |
| El span del servicio llamado **no tiene padre** (`parent=-`) | El contexto extraído no se usó al crear el span | Comparar `trace_id` de ambos servicios |
| El **baggage** llega vacío | No se inyectó el header `baggage` o el propagador no incluye `baggage` | Revisar `OTEL_PROPAGATORS` en ambos lados |
| Logs **sin** Trace ID | El log se emitió fuera de un span activo, o sin el bridge/correlación | Ver `TraceId`/`SpanId` vacíos en el debug exporter |

- Ambos lados deben usar **propagadores compatibles** (`OTEL_PROPAGATORS`, por defecto `tracecontext,baggage`).
- Prefiere las **librerías de instrumentación**: la propia documentación de Python lo recomienda porque están probadas ([Python · Propagation](https://opentelemetry.io/docs/languages/python/propagation/)).
- Revisa también lo que hay en medio (proxies o gateways): el contexto viaja en **headers HTTP**.

- [ ] Sé reconocer una traza partida y sus causas más comunes.
:::

:::step id="herramientas" title="Herramientas para depurar el Collector"
De [Troubleshooting](https://opentelemetry.io/docs/collector/troubleshooting/) e [Internal telemetry](https://opentelemetry.io/docs/collector/internal-telemetry/):

- **Telemetría interna**: métricas en formato Prometheus en el puerto **8888** (por defecto en `127.0.0.1:8888/metrics`) y logs en **stderr**. Métricas clave: `otelcol_receiver_accepted_*` y `otelcol_receiver_refused_*`, `otelcol_exporter_sent_*` y `otelcol_exporter_send_failed_*`, `otelcol_exporter_queue_size`/`_capacity`.
- **Debug exporter**: confirma que el Collector recibe, procesa y exporta. `verbosity`: `basic` (por defecto, un resumen), `normal` o `detailed` (el contenido completo); `sampling_initial` y `sampling_thereafter` limitan cuánto escribe ([README](https://github.com/open-telemetry/opentelemetry-collector/blob/main/exporter/debugexporter/README.md)).
- **zPages** (puerto **55679**): `/debug/tracez` (latencias, spans que no terminan, errores), `/debug/pipelinez`, `/debug/servicez`, `/debug/extensionz`, `/debug/featurez` ([README](https://github.com/open-telemetry/opentelemetry-collector/blob/main/extension/zpagesextension/README.md)).
- **pprof** (puerto **1777**): perfilado del Collector (caso avanzado).
- **health_check** (puerto **13133**): estado del Collector para sondas de vida/listo.
- `otelcol validate --config=…` y `otelcol components`.

**Checklist por cada salto** de un pipeline complejo: ¿hay errores en los logs del Collector? ¿cómo entra la telemetría? ¿cómo se modifica (sampling, redacción)? ¿cómo sale? ¿en qué formato? ¿cómo está configurado el siguiente salto? ¿hay políticas de red que lo impidan?

- [ ] Sé qué herramienta usar para cada pregunta del checklist.
:::

:::step id="problemas" title="Problemas comunes del Collector"
| Problema | Causas típicas (documentación oficial) |
|---|---|
| **No recibe** datos | Red; configuración del receiver o del cliente; el receiver está definido pero **no en un pipeline** |
| **No procesa** como esperas | Malentendido de cómo funciona el processor (p. ej., `attributes` solo actúa sobre atributos de spans; el nombre lo cambia el processor `span`; los processors de trazas, salvo tail sampling, trabajan span por span) |
| **No exporta** | Red (firewall, DNS, proxy); configuración del exporter; destino caído |
| **Pierde** datos | Collector mal dimensionado; destino lento o caído → ajustar reintentos y la cola de envío |
| **Se reinicia** | Presión de memoria sin `memory_limiter`; mal dimensionamiento; una cola más grande que la memoria; límites de la infraestructura |
| **Configuración** al combinar archivos | *Null maps*: usa `{}` para mapas vacíos |
:::

:::step id="errores" title="Manejo de errores y resiliencia"
**En los SDK** ([Error handling](https://opentelemetry.io/docs/specs/otel/error-handling/)):

- Las implementaciones **no deben lanzar excepciones no controladas en tiempo de ejecución**; la API no debe fallar aunque se use mal y debe usar valores seguros por defecto.
- Pueden **fallar rápido al iniciar** (p. ej., por una configuración inválida), pero no después.
- Los errores que se suprimen **deberían registrarse** (autodiagnóstico; nivel con `OTEL_LOG_LEVEL`). Por eso, en el Lab 7, un exporter mal configurado **no rompe la app**: solo escribe `StatusCode.UNAVAILABLE` en sus logs.

**En el Collector** ([exporterhelper](https://github.com/open-telemetry/opentelemetry-collector/blob/main/exporter/exporterhelper/README.md) y [Resiliency](https://opentelemetry.io/docs/collector/resiliency/)):

| Mecanismo | Valores por defecto |
|---|---|
| `retry_on_failure` | habilitado; `initial_interval` 5 s, `max_interval` 30 s, `max_elapsed_time` 300 s, `multiplier` 1.5 |
| `sending_queue` | habilitada; `num_consumers` 10, `queue_size` 1000 |
| Cola persistente | `sending_queue.storage` con una extensión como `file_storage` (sobrevive a reinicios) |

Se pierden datos si el destino cae más tiempo que `max_elapsed_time`, si la cola se llena, si el Collector se cae con cola solo en memoria, o si se deshabilitan colas y reintentos. Recomendación oficial: colas siempre en exporters de red, monitorear las métricas de cola y fallos, y concentrar la resiliencia en los saltos de red (agent → gateway → backend).

- [ ] Sé qué hace el SDK ante un error y qué protege al Collector de perder datos.
:::

:::step id="schemas" title="Telemetry schemas"
De [Telemetry Schemas](https://opentelemetry.io/docs/specs/otel/schemas/):

- Las **convenciones semánticas evolucionan** (p. ej., renombrar atributos). Sin un mecanismo de versionado, cambiar un nombre rompería a los consumidores que esperan el anterior.
- Un **telemetry schema** está **versionado** y define las **transformaciones** necesarias para convertir datos entre versiones (si no es posible convertir, es un cambio incompatible).
- Se identifica con un **Schema URL** cuya última parte es la versión: `https://opentelemetry.io/schemas/<version>`.
- Las fuentes (librerías de instrumentación) incluyen el **schema URL** en la telemetría; OTLP lo transporta en el campo `schema_url` a nivel de Resource y de Instrumentation Scope.
- Los consumidores pueden **transformar** los datos a la versión que esperan, o puede hacerlo un **Collector** intermedio cuando el backend no conoce los schemas.

Ejemplo práctico del curso: la migración de las convenciones HTTP en Python con `OTEL_SEMCONV_STABILITY_OPT_IN=http/dup` (emitir ambas versiones durante la transición) ([Python](https://opentelemetry.io/docs/languages/python/instrumentation/#semantic-convention-stability)).

- [ ] Puedo explicar para qué sirve un schema URL.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Collector · Troubleshooting](https://opentelemetry.io/docs/collector/troubleshooting/)
- [ ] [Internal telemetry](https://opentelemetry.io/docs/collector/internal-telemetry/)
- [ ] [Resiliency](https://opentelemetry.io/docs/collector/resiliency/)
- [ ] [Debug exporter (README)](https://github.com/open-telemetry/opentelemetry-collector/tree/main/exporter/debugexporter)
- [ ] [Telemetry schemas (especificación)](https://opentelemetry.io/docs/specs/otel/schemas/) y [Error handling](https://opentelemetry.io/docs/specs/otel/error-handling/)
- [ ] [Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) (repaso)
:::

:::step id="repaso" title="Puntos clave para repasar"
- Traza partida = falta inject o extract, o propagadores incompatibles.
- Puertos: métricas internas **8888**, zPages **55679**, pprof **1777**, health_check **13133**.
- Debug exporter: `basic` (por defecto), `normal`, `detailed`.
- Configurado pero fuera del pipeline = no hace nada.
- SDK: no lanza excepciones en tiempo de ejecución; registra los errores.
- Collector: `retry_on_failure` + `sending_queue` (+ cola persistente) contra la pérdida de datos.
- Schema URL versiona las convenciones para poder transformar entre versiones.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 11](../labs/lab11-depuracion.labguide.steps.md).
- [ ] Hice el [quiz del Dominio 4](../../tests/quiz-d4-depuracion.test.md).
:::
