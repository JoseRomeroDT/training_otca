---
title: "Laboratorio 5 · Métricas de negocio por OTLP"
description: "Instrumenta dice-server con cinco tipos de instrumento, exporta por OTLP al Collector y consulta en Prometheus; cambia la agregación de un histograma con una View y compara la temporalidad cumulative y delta."
slug: "lab05-metricas"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [lab, metricas, prometheus, views, temporalidad]
level: "intermediate"
objectives:
  - "Configurar MeterProvider con PeriodicExportingMetricReader y OTLPMetricExporter."
  - "Usar Counter, UpDownCounter, Histogram, Gauge y ObservableGauge."
  - "Consultar las métricas en Prometheus y entender la traducción de nombres."
  - "Cambiar la agregación con una View y comparar cumulative con delta."
prerequisites:
  - "Laboratorio 4 completado."
  - "Entorno levantado (labs/lab-env/up.sh)."
links:
  - label: "Sesión 5: material de estudio"
    url: "../estudio/s05-metricas.procedure.steps.md"
    icon: "book-open"
    highlight: true
  - label: "Código del laboratorio"
    url: "{{repo_url}}/tree/{{branch}}/labs/lab05-metricas"
    icon: "github"
  - label: "Metrics (oficial)"
    url: "https://opentelemetry.io/docs/concepts/signals/metrics/"
    icon: "external-link"
---

# {{ title }}

`dice_server.py` de este laboratorio es el del Lab 4 más métricas. El tráfico lo genera el mismo `player.py` del Lab 4.

| Instrumento | Nombre | Para qué |
|---|---|---|
| Counter | `dice.rolls` (`{roll}`) | Lanzamientos por valor |
| UpDownCounter | `dice.requests.active` | Requests en curso |
| Histogram | `dice.roll.duration` (`s`) | Duración de cada lanzamiento |
| Gauge | `dice.roll.last` | Último valor obtenido |
| ObservableGauge | `dice.players.known` | Jugadores distintos (callback) |

:::step id="levantar" title="Levantar y generar tráfico"
Si el servidor del Lab 4 sigue corriendo, detenlo. Terminal 1:

```bash
cd labs/lab05-metricas
python dice_server.py
```

Terminal 2:

```bash
cd labs/lab05-metricas
LAB_PARTIDAS=40 python ../lab04-trazas/player.py
```

- [ ] `player.py` termina con respuestas `HTTP 200`.
:::

:::step id="prometheus" title="Consultar en Prometheus"
Abre Prometheus (puerto 9090) → **Query**. Recuerda la traducción: `.` → `_`, sufijo `_total` en contadores y unidad como sufijo (`s` → `_seconds`).

```text
dice_rolls_total
sum by (dice_roll_value) (dice_rolls_total)
dice_requests_active
dice_roll_last
dice_players_known
histogram_quantile(0.95, sum by (le) (rate(dice_roll_duration_seconds_bucket[5m])))
```

- [ ] `dice_rolls_total` tiene una serie por cada valor de la etiqueta `dice_roll_value`.
- [ ] `dice_requests_active` vale 0 cuando no hay requests en curso (sube y baja).
- [ ] `dice_players_known` muestra los jugadores distintos (lo calcula un callback en cada recolección).
- [ ] El percentil 95 de la duración da unas centésimas de segundo (el código duerme entre 0,005 y 0,03 s por lanzamiento).
:::

:::step id="view" title="Agregación: con y sin View"
`dice_server.py` aplica una **View** al histograma con límites en segundos (`0.005, 0.01, 0.02, 0.03, 0.05, 0.1`). Mira los buckets:

```text
dice_roll_duration_seconds_bucket
```

Ahora reinicia el servidor **sin** la View y genera tráfico otra vez:

```bash
LAB_USAR_VIEW=0 python dice_server.py
```

- [ ] Con la View, las etiquetas `le` son los límites en segundos y los valores se reparten entre ellos.
- [ ] Sin la View aparecen los límites por defecto (`0, 5, 10, 25 … 10000`) y todos los valores caen en el primer tramo con datos: la distribución no sirve para calcular percentiles.
- [ ] Entiendo por qué la agregación por defecto depende de la unidad que elijas.

> [!NOTE]
> Durante unos minutos Prometheus puede mostrar a la vez los buckets viejos y los nuevos: el exporter `prometheus` del Collector conserva cada serie hasta 5 minutos sin actualizaciones (`metric_expiration`).
:::

:::step id="temporalidad" title="Cumulative frente a delta"
```bash
python temporalidad.py cumulative
python temporalidad.py delta
```

- [ ] En **cumulative** los valores exportados son 5, 10 y 15 (total desde el inicio).
- [ ] En **delta** son 5, 5 y 5 (solo lo ocurrido desde la exportación anterior).
- [ ] Sé que en Python la temporalidad por defecto de OTLP es cumulative y que se cambia con `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` ([Python · Exporters](https://opentelemetry.io/docs/languages/python/exporters/)).
:::

:::step id="cardinalidad" title="Piensa en la cardinalidad"
Si agregaras `player.name` como atributo de `dice.rolls`, ¿cuántas series tendrías con 10 000 jugadores? ¿Qué pasa al superar el límite por defecto de 2000 combinaciones? Repasa [Cardinality limits](https://opentelemetry.io/docs/concepts/signals/metrics/#cardinality-limits).

- [ ] Sé que al superarse el límite las mediciones van a un punto con `otel.metric.overflow=true`.
- [ ] Detuve `dice_server.py`.
:::
