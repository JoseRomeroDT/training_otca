---
title: "Sesión 5 · Métricas: instrumentos y agregación"
description: "MeterProvider y metric readers, los siete tipos de instrumento, agregación por defecto y Views, temporalidad cumulative/delta, límites de cardinalidad y exportación por OTLP. Dominio 2 (46 %)."
slug: "s05-metricas"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-2, metricas, agregacion, temporalidad]
duration: "2 horas"
level: "intermediate"
objectives:
  - "Configurar un MeterProvider con un metric reader y un exporter."
  - "Elegir el instrumento de métrica adecuado para cada caso."
  - "Comprender la agregación (por defecto y con Views) y la temporalidad."
  - "Exportar métricas por OTLP y entender su traducción a Prometheus."
links:
  - label: "Laboratorio 5: métricas"
    url: "../labs/lab05-metricas.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Metrics (concepto)"
    url: "https://opentelemetry.io/docs/concepts/signals/metrics/"
    icon: "book-open"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 2 · The OpenTelemetry API and SDK (46 %)** — competencias *Signals (Metric)*, *Data Model* y *SDK Pipelines*.

:::step id="pipeline" title="El pipeline de métricas"
De [Metrics](https://opentelemetry.io/docs/concepts/signals/metrics/) ([español](https://opentelemetry.io/es/docs/concepts/signals/metrics/)):

- Una **métrica** es una medición de un servicio capturada en tiempo de ejecución; el momento de la captura es un **metric event** (valor, momento y metadatos).
- **MeterProvider** → fábrica de **Meters** (se inicializa una vez, con Resource y exporters). Un **Meter** crea **instrumentos**.
- Un **metric reader** recolecta y entrega a un **exporter**. En Python: `PeriodicExportingMetricReader(exporter)`.
- El intervalo de exportación por defecto es **60000 ms** (`OTEL_METRIC_EXPORT_INTERVAL`) y el timeout **30000 ms** (`OTEL_METRIC_EXPORT_TIMEOUT`) ([SDK env vars](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/#periodic-exporting-metricreader)).

```python
reader = PeriodicExportingMetricReader(OTLPMetricExporter(endpoint="http://localhost:4317", insecure=True))
metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=[reader]))
meter = metrics.get_meter("lab05.dice_server", "1.1.0")
rolls = meter.create_counter("dice.rolls", unit="{roll}", description="Lanzamientos por valor")
rolls.add(1, {"dice.roll.value": 6})
```
:::

:::step id="instrumentos" title="Elegir el instrumento"
Un instrumento se define por **nombre**, **tipo**, **unidad** (opcional) y **descripción** (opcional). Los tipos ([Metrics · Instruments](https://opentelemetry.io/docs/concepts/signals/metrics/#metric-instruments)):

| Instrumento | Comportamiento | Ejemplo oficial |
|---|---|---|
| **Counter** | Acumula y **solo sube** | El odómetro de un auto |
| **Asynchronous Counter** | Como Counter, pero se lee una vez por exportación (callback) | Cuando solo tienes el total agregado |
| **UpDownCounter** | Acumula, puede **subir y bajar** | Largo de una cola |
| **Asynchronous UpDownCounter** | Como UpDownCounter, por callback | Tamaño actual de la cola |
| **Gauge** (síncrono) | Valor **actual** en el momento de leerlo | Indicador de combustible |
| **Asynchronous Gauge** | Valor actual, por callback | Versión de configuración activa |
| **Histogram** | Agregación en el cliente de una **distribución** de valores | Latencias: ¿cuántas requests tardan menos de 1 s? |

- **Síncronos**: se usan en línea con la lógica (al atender una request).
- **Asíncronos** (*observables*): registras un **callback** que el SDK invoca **al recolectar**; el callback debe respetar el timeout que recibe ([Python · Metrics](https://opentelemetry.io/docs/languages/python/instrumentation/#metrics)).

- [ ] Puedo elegir el instrumento para: requests atendidas, requests en curso, uso de memoria, latencia.
:::

:::step id="agregacion" title="Agregación y Views"
- Una **agregación** combina muchas mediciones en estadísticas exactas o estimadas de una ventana de tiempo; **OTLP transporta métricas ya agregadas**. Cada instrumento tiene una **agregación por defecto**, que se puede cambiar con **Views** ([Metrics · Aggregation](https://opentelemetry.io/docs/concepts/signals/metrics/#aggregation)).
- Agregación por defecto ([Metrics SDK · Default Aggregation](https://opentelemetry.io/docs/specs/otel/metrics/sdk/#default-aggregation)):

| Instrumento | Agregación por defecto |
|---|---|
| Counter, UpDownCounter y sus versiones asíncronas | **Sum** |
| Gauge y Asynchronous Gauge | **Last Value** |
| Histogram | **Explicit Bucket Histogram** con límites `0, 5, 10, 25, 50, 75, 100, 250, 500, 750, 1000, 2500, 5000, 7500, 10000` |

- Una **View** permite elegir qué instrumentos se procesan o ignoran, cambiar la agregación (p. ej. los límites de un histograma) y qué atributos se reportan ([Views](https://opentelemetry.io/docs/concepts/signals/metrics/#views)). En el laboratorio la usarás porque esos límites por defecto están pensados para milisegundos y tú medirás en segundos.

- [ ] Sé qué agregación usa cada instrumento y para qué sirve una View.
:::

:::step id="temporalidad" title="Temporalidad: cumulative y delta"
La **temporalidad de agregación** dice si cada punto informa el total **desde el inicio** (*cumulative*) o solo lo ocurrido **desde la exportación anterior** (*delta*) ([Metrics data model · Temporality](https://opentelemetry.io/docs/specs/otel/metrics/data-model/#temporality)).

- En Python el valor por defecto de `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` es **CUMULATIVE**; también acepta **DELTA** y **LOWMEMORY** ([Python · Exporters](https://opentelemetry.io/docs/languages/python/exporters/)):

| Instrumento | CUMULATIVE | DELTA | LOWMEMORY |
|---|---|---|---|
| Counter | Cumulative | Delta | Delta |
| UpDownCounter | Cumulative | Cumulative | Cumulative |
| Histogram | Cumulative | Delta | Delta |
| ObservableCounter | Cumulative | Delta | Cumulative |
| ObservableUpDownCounter | Cumulative | Cumulative | Cumulative |
| ObservableGauge | Cumulative | Cumulative | Cumulative |

- La elección importa al backend: al convertir a Prometheus, una suma monotónica **cumulative** pasa a ser un *Counter* de Prometheus; las *delta* **pueden** convertirse a cumulative ([compatibilidad con Prometheus](https://opentelemetry.io/docs/specs/otel/compatibility/prometheus_and_openmetrics/)).

- [ ] Puedo explicar con un ejemplo la diferencia entre cumulative y delta.
:::

:::step id="cardinalidad" title="Cardinalidad"
De [Metrics · Cardinality limits](https://opentelemetry.io/docs/concepts/signals/metrics/#cardinality-limits):

- La **cardinalidad** es el número de combinaciones distintas de atributos de una métrica; el SDK guarda un punto en memoria por cada una.
- Límite por defecto: **2000** combinaciones por métrica (se cambia con una View). Al superarlo, las mediciones nuevas se agregan en un **punto de desborde** con el atributo `otel.metric.overflow=true`: **no se pierden mediciones**, pero se pierden sus atributos.
- El límite **no** aplica a los atributos del **Resource** ni del **Instrumentation Scope**.
- Con **delta** el SDK libera el estado en cada ciclo; con **cumulative** lo conserva hasta reiniciar el proceso.
- Evita atributos de alta cardinalidad (IDs de usuario, rutas crudas con IDs).

- [ ] Sé qué pasa al superar el límite de cardinalidad.
:::

:::step id="otlp-prometheus" title="Exportar por OTLP y verlas en Prometheus"
En el laboratorio las métricas viajan **app → OTLP → Collector → exporter `prometheus` → Prometheus**. Reglas de traducción de nombres ([especificación](https://opentelemetry.io/docs/specs/otel/compatibility/prometheus_and_openmetrics/)):

- Los puntos (`.`) pasan a guion bajo (`_`).
- A una suma **monotónica** se le agrega el sufijo `_total`.
- La unidad se agrega como sufijo (`s` → `seconds`); las anotaciones entre llaves (`{roll}`) no.
- `service.name` se usa para la etiqueta `job`.

Ejemplo: `dice.rolls` (Counter, unidad `{roll}`) → `dice_rolls_total`; `dice.roll.duration` (Histogram, unidad `s`) → `dice_roll_duration_seconds_bucket`, `_sum` y `_count`.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Metrics (concepto)](https://opentelemetry.io/docs/concepts/signals/metrics/) · [español](https://opentelemetry.io/es/docs/concepts/signals/metrics/)
- [ ] [Python · Metrics](https://opentelemetry.io/docs/languages/python/instrumentation/#metrics)
- [ ] [Especificación de métricas](https://opentelemetry.io/docs/specs/otel/metrics/) (en particular *Data model* y *SDK*)
- [ ] [Ejemplos de métricas en opentelemetry-python](https://github.com/open-telemetry/opentelemetry-python/tree/main/docs/examples/metrics)
:::

:::step id="repaso" title="Puntos clave para repasar"
- 7 instrumentos: Counter, UpDownCounter, Gauge, Histogram (síncronos) y las versiones **asíncronas** de Counter, UpDownCounter y Gauge.
- Agregación por defecto: Sum (contadores), Last Value (gauges), Explicit Bucket Histogram (histogramas).
- Las **Views** cambian agregación, instrumentos y atributos.
- Exportación periódica por defecto: **60 s**.
- Python: temporalidad por defecto **cumulative**.
- Límite de cardinalidad por defecto **2000**; desborde en `otel.metric.overflow=true`.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 5](../labs/lab05-metricas.labguide.steps.md).
:::
