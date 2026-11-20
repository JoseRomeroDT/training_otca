---
title: "Sesión 2 · Instrumentación y convenciones semánticas"
description: "Instrumentación basada en código frente a zero-code, convenciones semánticas (y su migración a versiones estables), y cómo las señales sirven para SLI/SLO y los métodos RED y USE. Dominio 1 (18 %)."
slug: "s02-instrumentacion-semconv"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-1, instrumentacion, zero-code, semantic-conventions]
duration: "2,5 horas"
level: "beginner"
objectives:
  - "Aplicar convenciones semánticas a la telemetría (atributos de span y de recurso)."
  - "Distinguir instrumentación basada en código (manual) y zero-code (automática)."
  - "Relacionar las señales con SLI/SLO y con los métodos RED y USE."
  - "Interpretar qué resultados (outcomes) se obtienen al analizar la telemetría."
links:
  - label: "Laboratorio 2: zero-code en Python"
    url: "../labs/lab02-zero-code.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Quiz del Dominio 1"
    url: "../../tests/quiz-d1-fundamentos.test.md"
    icon: "graduation-cap"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 1 · Fundamentals of Observability (18 %)** — competencias *Semantic Conventions*, *Instrumentation* y *Analysis and Outcomes*.

:::step id="formas" title="Dos formas de instrumentar"
Según [Instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/) ([español](https://opentelemetry.io/es/docs/concepts/instrumentation/)), hay dos formas principales, **y se pueden usar a la vez**:

| | Basada en código (*code-based*) | Zero-code (automática) |
|---|---|---|
| Cómo | Usas la **API** y el **SDK** de OpenTelemetry en tu código | Un **agente** agrega la API y el SDK sin tocar el código |
| Qué ves | Telemetría rica de la **lógica de tu aplicación** | Lo que pasa en los **bordes**: requests HTTP, llamadas a bases de datos, colas |
| Cuándo | Para conocer a fondo tu aplicación | Para empezar rápido, o cuando no puedes modificar el código |

- La instrumentación zero-code usa mecanismos según el lenguaje: manipulación de *bytecode*, *monkey patching* o eBPF ([Zero-code](https://opentelemetry.io/docs/concepts/instrumentation/zero-code/)). En **Python** el agente usa *monkey patching* ([Python zero-code](https://opentelemetry.io/docs/zero-code/python/)).
- Para identificar tu servicio en el backend basta, para empezar, con configurar el **nombre del servicio**.
- Una **librería** debe depender solo de la **API**: sin SDK instalado, sus llamadas no tienen impacto. Una **aplicación** (proceso ejecutable) depende de la API **y** del SDK ([Code-based](https://opentelemetry.io/docs/concepts/instrumentation/code-based/)).
- Las **librerías de instrumentación** generan telemetría de librerías y frameworks populares; la meta del proyecto es que las librerías sean observables "de fábrica" (instrumentación nativa) ([Components](https://opentelemetry.io/docs/concepts/components/#instrumentation-libraries)).

En Python: `pip install opentelemetry-distro opentelemetry-exporter-otlp`, luego `opentelemetry-bootstrap -a install` (instala las instrumentaciones de los paquetes que detecta) y se ejecuta la app con `opentelemetry-instrument`.

- [ ] Puedo explicar cuándo usar cada tipo de instrumentación y que se combinan.
:::

:::step id="semconv" title="Convenciones semánticas"
Las [convenciones semánticas](https://opentelemetry.io/docs/concepts/semantic-conventions/) ([español](https://opentelemetry.io/es/docs/concepts/semantic-conventions/)) definen **nombres comunes** para tipos de operaciones y datos, para que la telemetría se pueda estandarizar entre bases de código, librerías y plataformas. Existen para **trazas, métricas, logs, profiles y recursos**.

Ejemplos de atributos HTTP actuales (tabla del [primer](https://opentelemetry.io/docs/concepts/observability-primer/#span-attributes)):

| Atributo | Ejemplo |
|---|---|
| `http.request.method` | `GET` |
| `url.path` | `/webshop/articles/4` |
| `http.route` | `/webshop/articles/:article_id` |
| `http.response.status_code` | `200` |
| `server.address` | `example.com` |
| `user_agent.original` | `Mozilla/5.0 …` |

**Recursos**: el SDK pone `service.name` (si no lo configuras vale `unknown_service`) y `telemetry.sdk.name`, `telemetry.sdk.language` y `telemetry.sdk.version`. Para el entorno se usa `deployment.environment.name` ([Resources](https://opentelemetry.io/docs/concepts/resources/)).

**Migración a convenciones estables.** Las instrumentaciones de Python siguen emitiendo por defecto los nombres experimentales anteriores (p. ej. `http.method`, `http.status_code`). Con `OTEL_SEMCONV_STABILITY_OPT_IN=http` emiten los estables, y con `http/dup` emiten ambos durante la transición ([Semantic convention stability](https://opentelemetry.io/docs/languages/python/instrumentation/#semantic-convention-stability)). Lo verás en el laboratorio.

- [ ] Sé qué son las convenciones semánticas y conozco los atributos HTTP más comunes.
:::

:::step id="sli-red-use" title="Señales, SLI/SLO, RED y USE"
- **SLI** mide el comportamiento del servicio desde la perspectiva del usuario; **SLO** comunica el objetivo de confiabilidad ligado al negocio ([primer](https://opentelemetry.io/docs/concepts/observability-primer/#reliability-and-metrics)).
- **RED** = *Rate, Errors, Duration*: tasa de solicitudes, errores y duración, por servicio u operación. En el Collector, el connector `span_metrics` "agrega métricas R.E.D. a partir de los spans" ([README oficial](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector)). Fuente original del método: [The RED Method (Tom Wilkie)](https://grafana.com/blog/the-red-method-how-to-instrument-your-services/).
- **USE** = *Utilization, Saturation, Errors*: utilización, saturación y errores, por **recurso** (CPU, memoria, disco, red). Fuente original: [The USE Method (Brendan Gregg)](https://www.brendangregg.com/usemethod.html).

Relación práctica: los SLI de un servicio (latencia, tasa de error) suelen salir de métricas RED; las causas de infraestructura se buscan con métricas USE; las **trazas** muestran *dónde* ocurre el problema y los **logs correlacionados** el *detalle*.
:::

:::step id="outcomes" title="Analysis and outcomes: qué se obtiene de la telemetría"
La competencia *Analysis and Outcomes* trata de qué decisiones permite la telemetría. En la documentación oficial:

- **Correlación**: con [context propagation](https://opentelemetry.io/docs/concepts/context-propagation/) las señales se relacionan sin importar dónde se generen: los logs llevan el Trace ID y el Span ID, y las métricas se pueden agregar por contexto (p. ej., `GET /checkout > GET /product`).
- **Diagnóstico de problemas nuevos**: la observabilidad responde "¿por qué está pasando?" ([primer](https://opentelemetry.io/docs/concepts/observability-primer/)).
- **Costo frente a visibilidad**: el [sampling](https://opentelemetry.io/docs/concepts/sampling/) reduce costos manteniendo una muestra representativa.
- **Escalar o alertar**: los datos de métricas pueden alertar de una caída o disparar decisiones de escalado automático ([Metrics](https://opentelemetry.io/docs/concepts/signals/metrics/)).

- [ ] Puedo relacionar cada señal con el tipo de decisión que habilita.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Semantic conventions (concepto)](https://opentelemetry.io/docs/concepts/semantic-conventions/) · [español](https://opentelemetry.io/es/docs/concepts/semantic-conventions/)
- [ ] [Convenciones HTTP para spans](https://opentelemetry.io/docs/specs/semconv/http/http-spans/) y el [repositorio de semantic-conventions](https://github.com/open-telemetry/semantic-conventions)
- [ ] [Instrumentation: code-based y zero-code](https://opentelemetry.io/docs/concepts/instrumentation/) · [español](https://opentelemetry.io/es/docs/concepts/instrumentation/)
- [ ] [Zero-code en Python](https://opentelemetry.io/docs/zero-code/python/) · [español](https://opentelemetry.io/es/docs/zero-code/python/)
- [ ] [Getting Started de Python](https://opentelemetry.io/docs/languages/python/getting-started/)
- [ ] [Resources](https://opentelemetry.io/docs/concepts/resources/) · [español](https://opentelemetry.io/es/docs/concepts/resources/)
:::

:::step id="repaso" title="Puntos clave para repasar"
- Code-based y zero-code **no se excluyen**: lo normal es combinarlos.
- Zero-code instrumenta **librerías** (los bordes), no tu lógica de negocio.
- Las librerías dependen solo de la **API**; las aplicaciones, de API **y** SDK.
- `service.name` es el atributo de recurso clave; sin configurarlo vale `unknown_service`.
- Las convenciones semánticas existen para trazas, métricas, logs, profiles y recursos.
- RED → servicios (*Rate, Errors, Duration*); USE → recursos (*Utilization, Saturation, Errors*).

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 2](../labs/lab02-zero-code.labguide.steps.md).
- [ ] Hice el [quiz del Dominio 1](../../tests/quiz-d1-fundamentos.test.md).
:::
