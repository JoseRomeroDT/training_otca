---
title: "Quiz Dominio 2 · The OpenTelemetry API and SDK"
description: "20 preguntas sobre API y SDK, modelo de datos, trazas, métricas, logs, propagación de contexto, configuración, OTLP y agentes (46 % del examen). Cada explicación cita la documentación oficial."
slug: "quiz-d2-api-sdk"
type: "test"
version: "1.0.0"
updated: "2026-11-20"
tags: [quiz, dominio-2, otca]
level: "intermediate"
passingScore: 75
feedback: "immediate"
shuffle: true
---

# {{ title }}

El dominio con más peso del examen. Umbral: **75 %**.

:::question id="d2-noop" type="single"
Una aplicación usa una librería instrumentada con la API de OpenTelemetry, pero **no** instala ningún SDK. ¿Qué ocurre?
- [ ] La aplicación falla al iniciar porque falta el SDK
- [x] Las llamadas a la API son no-op: devuelven objetos válidos, no fallan y no se emite telemetría
- [ ] La API envía la telemetría directamente al Collector local
- [ ] La API guarda la telemetría en memoria hasta que se instale un SDK
:::explanation
Sin SDK, la API usa una implementación mínima que devuelve objetos válidos con un costo mínimo y no entrega telemetría. Fuente: [Library guidelines · API and minimal implementation](https://opentelemetry.io/docs/specs/otel/library-guidelines/#api-and-minimal-implementation).
:::
:::

:::question id="d2-default-sampler" type="single"
¿Cuál es el sampler por defecto del SDK de trazas?
- [ ] `AlwaysOn`
- [ ] `TraceIdRatioBased(0.5)`
- [x] `ParentBased(root=AlwaysOn)`
- [ ] `AlwaysOff`
:::explanation
La especificación del SDK fija como valor por defecto `ParentBased(root=AlwaysOn)` (`parentbased_always_on` en `OTEL_TRACES_SAMPLER`). Fuente: [Trace SDK · Built-in samplers](https://opentelemetry.io/docs/specs/otel/trace/sdk/#built-in-samplers).
:::
:::

:::question id="d2-parentbased" type="single"
Un servicio usa `ParentBased(root=TraceIdRatioBased(0.0))`. Le llega una solicitud cuyo `traceparent` indica que el padre remoto **sí** fue muestreado. ¿Qué pasa con el span del servicio?
- [ ] Se descarta, porque el ratio raíz es 0
- [x] Se muestrea, porque con padre remoto muestreado ParentBased usa AlwaysOn por defecto
- [ ] Se muestrea con probabilidad 0,5
- [ ] Depende del exporter configurado
:::explanation
`ParentBased` solo usa el sampler `root` cuando no hay padre; con padre remoto muestreado usa `remoteParentSampled`, que por defecto es AlwaysOn. Fuente: [Trace SDK · ParentBased](https://opentelemetry.io/docs/specs/otel/trace/sdk/#parentbased).
:::
:::

:::question id="d2-bsp-delay" type="number" answer="5000"
¿Cuál es el valor por defecto, en milisegundos, de `OTEL_BSP_SCHEDULE_DELAY` (demora entre dos exportaciones del Batch Span Processor)?
:::explanation
5000 ms. Los demás valores por defecto: cola 2048, lote 512 y timeout 30000 ms. Fuente: [SDK environment variables · Batch Span Processor](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#batch-span-processor).
:::
:::

:::question id="d2-status" type="single"
Un span terminó sin errores y nadie le asignó un estado. ¿Cuál es su estado?
- [x] `Unset`
- [ ] `Ok`
- [ ] `Error`
- [ ] No tiene estado
:::explanation
El valor por defecto es `Unset` y significa que terminó sin error; `Ok` solo se usa cuando el desarrollador lo marca explícitamente. Fuente: [Traces · Span Status](https://opentelemetry.io/docs/concepts/signals/traces/#span-status).
:::
:::

:::question id="d2-kind" type="single"
Si al crear un span no se indica su *kind*, ¿cuál se asume?
- [ ] `Server`
- [ ] `Client`
- [x] `Internal`
- [ ] `Producer`
:::explanation
Si no se indica, el span kind se asume `Internal`. Fuente: [Traces · Span Kind](https://opentelemetry.io/docs/concepts/signals/traces/#span-kind).
:::
:::

:::question id="d2-evento" type="single"
Según la guía oficial, ¿cuándo conviene registrar un dato como **evento de span** en lugar de como atributo?
- [ ] Cuando el dato es numérico
- [x] Cuando el momento (timestamp) en que ocurrió es significativo
- [ ] Cuando el dato debe usarse para el sampling
- [ ] Nunca: los eventos están obsoletos
:::explanation
Si el timestamp importa, usa un evento; si no, un atributo. Fuente: [Traces · When to use span events versus span attributes](https://opentelemetry.io/docs/concepts/signals/traces/#when-to-use-span-events-versus-span-attributes).
:::
:::

:::question id="d2-links" type="single"
Una operación se encola y se procesa más tarde, de forma asíncrona, en otra traza. ¿Qué mecanismo asocia causalmente ambas trazas?
- [ ] Un atributo con el nombre de la cola
- [x] Un span link
- [ ] El baggage
- [ ] Un span de tipo `Internal`
:::explanation
Los links asocian un span con otros spans con relación causal, típico en operaciones asíncronas. Fuente: [Traces · Span Links](https://opentelemetry.io/docs/concepts/signals/traces/#span-links).
:::
:::

:::question id="d2-instrumentos" type="match"
Relaciona cada caso con el instrumento más adecuado:

- Total de solicitudes atendidas :: Counter
- Solicitudes en curso en este momento :: UpDownCounter
- Distribución de la latencia de las solicitudes :: Histogram
- Uso de memoria leído por callback en cada recolección :: Asynchronous Gauge
:::explanation
Counter solo sube; UpDownCounter sube y baja; Histogram describe distribuciones; los asíncronos se leen con callback en cada recolección. Fuente: [Metrics · Metric Instruments](https://opentelemetry.io/docs/concepts/signals/metrics/#metric-instruments).
:::
:::

:::question id="d2-agregacion" type="single"
¿Qué agregación usa el SDK por defecto para un **Gauge**?
- [ ] Sum
- [x] Last Value
- [ ] Explicit Bucket Histogram
- [ ] Exponential Histogram
:::explanation
Contadores → Sum; Gauges → Last Value; Histogram → Explicit Bucket Histogram. Fuente: [Metrics SDK · Default Aggregation](https://opentelemetry.io/docs/specs/otel/metrics/sdk/#default-aggregation).
:::
:::

:::question id="d2-view" type="single"
Necesitas cambiar los límites de los buckets de un histograma sin tocar el código que registra las mediciones. ¿Qué usas?
- [ ] Un nuevo instrumento
- [x] Una View
- [ ] Un span processor
- [ ] La variable `OTEL_METRIC_EXPORT_INTERVAL`
:::explanation
Las Views personalizan qué instrumentos se procesan, la agregación y los atributos reportados. Fuente: [Metrics · Views](https://opentelemetry.io/docs/concepts/signals/metrics/#views).
:::
:::

:::question id="d2-temporalidad" type="single"
Un Counter recibe `add(5)` tres veces, una entre cada exportación. Con temporalidad **delta**, ¿qué valores se exportan?
- [ ] 5, 10, 15
- [x] 5, 5, 5
- [ ] 15, 15, 15
- [ ] 0, 5, 10
:::explanation
Delta informa solo lo ocurrido desde la exportación anterior; cumulative informaría 5, 10, 15. Fuente: [Metrics data model · Temporality](https://opentelemetry.io/docs/specs/otel/metrics/data-model/#temporality).
:::
:::

:::question id="d2-cardinalidad" type="single"
Una métrica supera el límite de cardinalidad por defecto. ¿Qué ocurre con las nuevas combinaciones de atributos?
- [ ] Se descartan las mediciones
- [ ] El SDK lanza una excepción
- [x] Se agregan en un punto de desborde con el atributo `otel.metric.overflow=true`
- [ ] Se exportan como logs
:::explanation
Límite por defecto: 2000 combinaciones por métrica. No se pierden mediciones, pero sí sus atributos. Fuente: [Metrics · Cardinality limits](https://opentelemetry.io/docs/concepts/signals/metrics/#cardinality-limits).
:::
:::

:::question id="d2-intervalo" type="number" answer="60000"
¿Cuál es el intervalo por defecto, en milisegundos, entre exportaciones del metric reader periódico (`OTEL_METRIC_EXPORT_INTERVAL`)?
:::explanation
60000 ms (60 s). Fuente: [SDK environment variables · Periodic exporting MetricReader](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#periodic-exporting-metricreader).
:::
:::

:::question id="d2-bridge" type="single"
¿Quién debería usar directamente la **Logs Bridge API**?
- [ ] Todo desarrollador que quiera emitir logs
- [x] Los autores de librerías de logging que construyen appenders o bridges
- [ ] El Collector, para recibir logs
- [ ] Solo los backends de observabilidad
:::explanation
Como desarrollador usas tu librería de logging con un appender/bridge; la Bridge API es para quienes escriben esos appenders. Fuente: [Logs · Log Appender / Bridge](https://opentelemetry.io/docs/concepts/signals/logs/#log-appender--bridge).
:::
:::

:::question id="d2-propagacion-orden" type="order"
Ordena los pasos de la propagación manual de contexto entre dos servicios HTTP:

1. El servicio A crea su span y lo hace actual
2. El servicio A inyecta el contexto en los headers (inject)
3. El servicio A envía la solicitud HTTP con esos headers
4. El servicio B extrae el contexto de los headers (extract)
5. El servicio B crea su span usando el contexto extraído como padre
:::explanation
Emisor: inject en el carrier; receptor: extract y uso como padre. Fuente: [Context propagation · Custom context propagation](https://opentelemetry.io/docs/concepts/context-propagation/#custom-context-propagation).
:::
:::

:::question id="d2-propagadores" type="single"
¿Qué propagadores usa por defecto un SDK de OpenTelemetry (`OTEL_PROPAGATORS`)?
- [ ] `b3`
- [ ] `jaeger`
- [x] `tracecontext,baggage`
- [ ] `none`
:::explanation
El valor por defecto es `tracecontext,baggage` (W3C Trace Context y W3C Baggage). Fuente: [SDK environment variables](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#general-sdk-configuration).
:::
:::

:::question id="d2-baggage" type="true-false" answer="false"
Los valores del baggage se agregan automáticamente como atributos de todos los spans, métricas y logs.
:::explanation
El baggage es un almacén separado: hay que leerlo y agregarlo explícitamente (algunos lenguajes ofrecen Baggage Span Processors que lo hacen). Fuente: [Baggage · Baggage is not the same as attributes](https://opentelemetry.io/docs/concepts/signals/baggage/#baggage-is-not-the-same-as-attributes).
:::
:::

:::question id="d2-otlp-http" type="single"
Con `OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf` y `OTEL_EXPORTER_OTLP_ENDPOINT=http://collector:4318`, ¿a qué URL envía el SDK las trazas?
- [ ] `http://collector:4318`
- [x] `http://collector:4318/v1/traces`
- [ ] `http://collector:4317/v1/traces`
- [ ] `http://collector:4318/traces`
:::explanation
Con el endpoint base y HTTP, el SDK agrega la ruta de cada señal (`/v1/traces`, `/v1/metrics`, `/v1/logs`); los endpoints por señal (`OTEL_EXPORTER_OTLP_TRACES_ENDPOINT`) se usan tal cual. Fuente: [OTLP exporter configuration](https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/).
:::
:::

:::question id="d2-reintentos" type="multiple"
En OTLP/HTTP, ¿qué códigos de respuesta deben **reintentarse**? Marca todos.
- [x] 429 Too Many Requests
- [x] 502 Bad Gateway
- [x] 503 Service Unavailable
- [x] 504 Gateway Timeout
- [ ] 400 Bad Request
:::explanation
Solo 429, 502, 503 y 504; el resto de códigos 4xx y 5xx no se reintentan (400 indica datos inválidos). Fuente: [Especificación OTLP · Retryable response codes](https://opentelemetry.io/docs/specs/otlp/#retryable-response-codes).
:::
:::
