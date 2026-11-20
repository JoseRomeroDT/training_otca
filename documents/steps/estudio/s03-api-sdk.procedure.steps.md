---
title: "Sesión 3 · API vs SDK y modelo de datos"
description: "La separación entre API y SDK, la implementación mínima no-op, los providers, el modelo de datos (Resource, Instrumentation Scope y cada señal) y cómo se compone y extiende el SDK. Dominio 2 (46 %)."
slug: "s03-api-sdk"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-2, api, sdk, data-model]
duration: "2 horas"
level: "intermediate"
objectives:
  - "Explicar la separación API/SDK y por qué la API es no-op sin SDK."
  - "Describir el modelo de datos de OpenTelemetry: Resource, Instrumentation Scope y los datos de cada señal."
  - "Configurar el SDK sobre la API: providers, processors y exporters."
  - "Comprender cómo se compone y extiende el SDK (processors propios, distribuciones)."
links:
  - label: "Laboratorio 3: API y SDK"
    url: "../labs/lab03-api-sdk.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Library guidelines (especificación)"
    url: "https://opentelemetry.io/docs/specs/otel/library-guidelines/"
    icon: "book-open"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 2 · The OpenTelemetry API and SDK (46 %)** — el dominio con más peso del examen. Competencias de esta sesión: *Data Model* y *Composability and Extension*.

:::step id="especificacion" title="Qué define la especificación"
La [especificación](https://opentelemetry.io/docs/specs/otel/) describe los requisitos para todas las implementaciones ([Components](https://opentelemetry.io/docs/concepts/components/#specification), [español](https://opentelemetry.io/es/docs/concepts/components/)):

- **API**: tipos de datos y operaciones para **generar y correlacionar** trazas, métricas y logs.
- **SDK**: los requisitos de la implementación en cada lenguaje: **configuración, procesamiento y exportación**.
- **Data**: el protocolo **OTLP** y las **convenciones semánticas**.

El cliente de OpenTelemetry tiene cuatro tipos de paquetes: **API**, **SDK**, **convenciones semánticas** y **plugins** (*contrib*) ([Library guidelines](https://opentelemetry.io/docs/specs/otel/library-guidelines/)).
:::

:::step id="noop" title="API sin SDK: la implementación mínima (no-op)"
De las [Library guidelines](https://opentelemetry.io/docs/specs/otel/library-guidelines/#api-and-minimal-implementation):

- Las librerías y frameworks que se quieren instrumentar dependen **solo de la API**. La **aplicación** decide si instala el SDK.
- Si **no** hay SDK, las llamadas a la API son **no-ops** con un costo mínimo: la aplicación compila y corre, pero no se entrega telemetría.
- La implementación mínima devuelve **objetos válidos** (por ejemplo, crear un span no falla y devuelve un span no nulo), así el código instrumentado no necesita comprobaciones extra.
- El **SDK es una dependencia separada y opcional**: al instalarlo, **sustituye** la implementación mínima.
- Las versiones de la API y del SDK son **independientes** entre sí (y de la versión de la especificación).

En el laboratorio verás que, sin SDK, Python devuelve un `NonRecordingSpan` que no graba nada y cuyo `SpanContext` no es válido.

Relacionado (lo retomarás en la Sesión 11): las implementaciones **no deben lanzar excepciones no controladas en tiempo de ejecución**; pueden fallar al iniciar por una mala configuración, pero no después ([Error handling](https://opentelemetry.io/docs/specs/otel/error-handling/)).

- [ ] Puedo explicar por qué una librería instrumentada no obliga a usar OpenTelemetry.
:::

:::step id="providers" title="Providers, tracers, meters y loggers"
- Un **TracerProvider** (y su equivalente **MeterProvider** / **LoggerProvider**) es una **fábrica** de *tracers* (*meters* / *loggers*). Normalmente se inicializa **una vez** y vive lo mismo que la aplicación; al inicializarlo se configuran también el **Resource** y los **exporters**. Suele registrarse como proveedor **global** ([Traces](https://opentelemetry.io/docs/concepts/signals/traces/#tracer-provider), [Metrics](https://opentelemetry.io/docs/concepts/signals/metrics/#meter-provider)).
- Un **Tracer** crea spans; un **Meter** crea instrumentos de métricas.
- Al pedir un tracer o meter se le da un **nombre** (y una versión) que identifica **qué se está instrumentando**: ese es el **Instrumentation Scope** ([Code-based](https://opentelemetry.io/docs/concepts/instrumentation/code-based/)).
- En **logs**, la aplicación **no** usa una "Logs API" propia: usa su librería de logging habitual y un **appender/bridge** que envía los registros al SDK. La *Logs Bridge API* es para autores de librerías de logging ([Logs](https://opentelemetry.io/docs/concepts/signals/logs/#log-appender--bridge)).

```python
# Configuración del SDK (una vez, al iniciar)
provider = TracerProvider(resource=Resource.create({"service.name": "dice-server"}))
provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
trace.set_tracer_provider(provider)

# Uso de la API (en cualquier módulo)
tracer = trace.get_tracer("mi.modulo", "1.0.0")
```

Fuente: [Python · Instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/).

- [ ] Sé qué se configura una vez (SDK) y qué se usa en todo el código (API).
:::

:::step id="datamodel" title="El modelo de datos"
Toda la telemetría se agrupa así (es la estructura que transporta OTLP):

```text
Resource            → QUIÉN produce la telemetría (service.name, host, k8s.pod.name…)
└─ Instrumentation Scope → QUÉ librería o módulo la produjo (name, version, schema_url, attributes)
   └─ spans | puntos de métricas | log records
```

- **Resource**: la entidad que produce la telemetría. Se asocia al provider al crearlo y **no se puede cambiar después** ([Resources](https://opentelemetry.io/docs/concepts/resources/)).
- **Instrumentation Scope**: unidad lógica de software asociada a la telemetría, identificada por `(name, version, schema_url, attributes)` ([Instrumentation scope](https://opentelemetry.io/docs/concepts/instrumentation-scope/)).
- **Atributos**: claves de tipo texto no nulas; valores texto, booleano, número de punto flotante, entero o arreglos de esos tipos ([Traces · Attributes](https://opentelemetry.io/docs/concepts/signals/traces/#attributes)).
- **Span**: nombre, ID del span padre (vacío en el root span), inicio y fin, *Span Context* (Trace ID, Span ID, Trace Flags, Trace State), atributos, eventos, links, estado y *kind* ([Traces](https://opentelemetry.io/docs/concepts/signals/traces/#spans)).
- **Métricas**: tipos de punto `Sum`, `Gauge`, `Histogram`, `ExponentialHistogram` y `Summary` (este último solo por compatibilidad, *legacy*) ([Metrics data model](https://opentelemetry.io/docs/specs/otel/metrics/data-model/)).
- **Log record**: Timestamp, ObservedTimestamp, TraceId, SpanId, TraceFlags, SeverityText, SeverityNumber, Body, Resource, InstrumentationScope, Attributes y EventName ([Logs · Log Record](https://opentelemetry.io/docs/concepts/signals/logs/#log-record)).

- [ ] Puedo dibujar la jerarquía Resource → Scope → datos y decir qué va en cada nivel.
:::

:::step id="extension" title="Composición y extensión"
El SDK está hecho de piezas intercambiables con interfaces definidas por la especificación:

- **Span processors**: el SDK debe traer un **simple** (exporta cada span al terminar) y un **batch** (exporta en lotes) ([Trace SDK](https://opentelemetry.io/docs/specs/otel/trace/sdk/#built-in-span-processors)). Un provider puede tener **varios** processors y puedes escribir los tuyos.
- **Exporters**, **samplers**, **generadores de IDs**, **detectores de recursos** y **propagadores** también son reemplazables ([Components](https://opentelemetry.io/docs/concepts/components/)).
- En métricas, las **Views** personalizan qué instrumentos se procesan, la agregación y los atributos ([Metrics · Views](https://opentelemetry.io/docs/concepts/signals/metrics/#views)).
- Una **distribución** es una versión personalizada de un componente de OpenTelemetry (no un *fork*): *pure* (misma funcionalidad), *plus* (agrega componentes) o *minus* (quita componentes) ([Distributions](https://opentelemetry.io/docs/concepts/distributions/), [español](https://opentelemetry.io/es/docs/concepts/distributions/)).

- [ ] Sé qué partes del SDK puedo reemplazar o agregar.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Components](https://opentelemetry.io/docs/concepts/components/) · [español](https://opentelemetry.io/es/docs/concepts/components/)
- [ ] [Library guidelines (especificación)](https://opentelemetry.io/docs/specs/otel/library-guidelines/)
- [ ] [OpenTelemetry Python](https://opentelemetry.io/docs/languages/python/) y su [Instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/) · [español](https://opentelemetry.io/es/docs/languages/python/instrumentation/)
- [ ] [Resources](https://opentelemetry.io/docs/concepts/resources/) e [Instrumentation scope](https://opentelemetry.io/docs/concepts/instrumentation-scope/)
- [ ] Repositorio [opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python)
:::

:::step id="repaso" title="Puntos clave para repasar"
- Librerías → solo **API**. Aplicaciones → API **+ SDK**.
- Sin SDK la API es **no-op**: no falla y no emite telemetría.
- El **provider** se configura una vez e incluye Resource y exporters; el **Resource** no cambia después.
- Jerarquía de datos: **Resource → Instrumentation Scope → datos de la señal**.
- El SDK trae processors **simple** y **batch**; se pueden encadenar varios y escribir propios.
- Distribuciones: **pure, plus, minus**.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 3](../labs/lab03-api-sdk.labguide.steps.md).
:::
