---
title: "Sesión 8 · Collector: componentes y pipelines"
description: "Qué es el OpenTelemetry Collector y cuándo usarlo, sus distribuciones, la estructura de su configuración (receivers, processors, exporters, connectors, extensions y service), los pipelines por señal y cómo validar una configuración. Dominio 3 (26 %)."
slug: "s08-collector"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-3, collector, pipelines, configuracion]
level: "intermediate"
objectives:
  - "Describir receivers, processors, exporters, connectors y extensions."
  - "Construir pipelines de servicio por señal."
  - "Escribir y validar el archivo de configuración del Collector."
  - "Enrutar telemetría a uno o más backends."
links:
  - label: "Laboratorio 8: tu propio Collector"
    url: "../labs/lab08-collector.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Collector · Configuration"
    url: "https://opentelemetry.io/docs/collector/configuration/"
    icon: "book-open"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 3 · The OpenTelemetry Collector (26 %)** — competencias *Configuration* y *Pipelines*.

:::step id="que-es" title="Qué es y cuándo usarlo"
De [Collector](https://opentelemetry.io/docs/collector/):

- Es una implementación **agnóstica de proveedor** para **recibir, procesar y exportar** telemetría. Evita operar varios agentes y soporta formatos open source (Jaeger, Prometheus, Fluent Bit…) hacia uno o varios backends.
- Para empezar o en entornos pequeños puedes enviar directo al backend, pero **en general se recomienda usar un Collector** junto a tus servicios: la app descarga rápido sus datos y el Collector se encarga de **reintentos, batching, cifrado y filtrado de datos sensibles**.
- Los exporters OTLP de los SDK apuntan por defecto a un Collector **local**.
- **Distribuciones** oficiales (versión 0.165.0): `otelcol` (core), `otelcol-contrib`, `otelcol-k8s`, `otelcol-otlp`, entre otras; los componentes de cada una están en su `manifest.yaml`. Con **ocb** (*OpenTelemetry Collector Builder*) construyes la tuya ([Distributions](https://opentelemetry.io/docs/collector/distributions/)).
- Cada componente tiene su propio **nivel de estabilidad** (en su README); el Collector en conjunto tiene estado *mixed*.

- [ ] Sé explicar por qué conviene poner un Collector entre las apps y el backend.
:::

:::step id="componentes" title="Los componentes"
De [Configuration](https://opentelemetry.io/docs/collector/configuration/) y [Components](https://opentelemetry.io/docs/collector/components/) ([español](https://opentelemetry.io/es/docs/collector/components/)):

| Componente | Qué hace | Ejemplos |
|---|---|---|
| **Receivers** | Recolectan datos, por *push* o *pull* | `otlp`, `prometheus`, `file_log`, `host_metrics`, `zipkin` |
| **Processors** | Modifican, filtran, muestrean o enriquecen | `memory_limiter`, `batch`, `attributes`, `resource`, `filter`, `transform`, `probabilistic_sampler` |
| **Exporters** | Envían a uno o más destinos | `otlp_grpc`, `otlp_http`, `debug`, `prometheus`, `file` |
| **Connectors** | Unen dos pipelines: son **exporter** de uno y **receiver** de otro | `count`, `span_metrics`, `routing`, `forward` |
| **Extensions** | Capacidades que **no** tocan la telemetría | `health_check`, `zpages`, `pprof`, autenticación |

- Los identificadores siguen el formato `tipo[/nombre]`, p. ej. `otlp` u `otlp_grpc/jaeger`: puedes tener varias instancias del mismo tipo.
- **Configurar un componente no lo activa**: los receivers, processors, exporters y connectors se activan en `service.pipelines`; las extensions, en `service.extensions`.
- El Collector, por seguridad, escucha en **`localhost`** por defecto; los ejemplos oficiales usan `0.0.0.0` por comodidad (necesario dentro de contenedores).

> [!NOTE]
> Nombres en versiones recientes: el exporter `otlp` pasó a llamarse **`otlp_grpc`** y `otlphttp` pasó a **`otlp_http`** (los nombres viejos siguen funcionando como *deprecated*). También `hostmetrics` → `host_metrics`, `filelog` → `file_log`, `spanmetrics` → `span_metrics`, `k8sattributes` → `k8s_attributes`. Verificado en el código del Collector v0.165.0; material más antiguo usa los nombres viejos.

- [ ] Puedo clasificar cualquier componente en una de las cinco categorías.
:::

:::step id="service" title="La sección service y los pipelines"
```yaml
service:
  extensions: [health_check, zpages]
  telemetry: { ... }                  # observabilidad del propio Collector
  pipelines:
    traces:
      receivers: [otlp]
      processors: [memory_limiter, batch]   # el ORDEN importa
      exporters: [otlp_grpc/jaeger, debug]
    metrics:
      receivers: [otlp]
      exporters: [prometheus]
    traces/2:                          # otro pipeline del mismo tipo
      receivers: [otlp/2]
      exporters: [zipkin]
```

De [Architecture](https://opentelemetry.io/docs/collector/architecture/):

- Un pipeline es de un tipo de señal (`traces`, `metrics`, `logs`) y tiene receivers, processors **opcionales** y exporters.
- Un mismo receiver puede estar en varios pipelines: se crea **una sola instancia** que reparte los datos (*fan-out*); si un processor bloquea, bloquea a los demás pipelines de ese receiver.
- Un mismo processor referenciado en varios pipelines crea **una instancia por pipeline** (cada una con su propio estado).
- Varios pipelines pueden compartir un exporter.

**Orden recomendado de processors** ([recommended processors](https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/README.md#recommended-processors)): 1) `memory_limiter` primero; 2) sampling o filtrado; 3) los que dependen del contexto de origen (p. ej. `k8s_attributes`); 4) transformación y enriquecimiento; 5) `batch` al final. Hoy se recomienda además **preferir el batching del exporter** (`sending_queue.batch`) cuando esté disponible.

- [ ] Sé armar un pipeline por señal y en qué orden van los processors.
:::

:::step id="archivo" title="El archivo de configuración"
- Ubicación por defecto: `/etc/<otel-directory>/config.yaml` (p. ej. `/etc/otelcol-contrib/config.yaml`). Se indica con `--config`, que acepta archivos o URIs con proveedores `file`, `env`, `yaml`, `http` y `https`; se pueden pasar **varios** `--config` y se combinan ([Location](https://opentelemetry.io/docs/collector/configuration/#location)).
- **Validar** antes de desplegar: `otelcol validate --config=archivo.yaml`.
- **Variables de entorno**: `${env:DB_KEY}` y con valor por defecto `${env:DB_KEY:-valor}`; `$$` es un `$` literal ([Environment variables](https://opentelemetry.io/docs/collector/configuration/#environment-variables)).
- `otelcol components` lista los componentes de una distribución y su estabilidad ([Troubleshooting](https://opentelemetry.io/docs/collector/troubleshooting/#check-collector-components)).
- Al combinar varias configuraciones, los mapas se fusionan y los **arreglos se reemplazan**; usa `{}` para mapas vacíos (*null maps*).

- [ ] Sé validar una configuración y usar variables de entorno en ella.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Collector (introducción)](https://opentelemetry.io/docs/collector/)
- [ ] [Configuration](https://opentelemetry.io/docs/collector/configuration/) (completa: es la página más importante del dominio)
- [ ] [Architecture](https://opentelemetry.io/docs/collector/architecture/)
- [ ] [Components](https://opentelemetry.io/docs/collector/components/) · [español](https://opentelemetry.io/es/docs/collector/components/)
- [ ] [Quick start](https://opentelemetry.io/docs/collector/quick-start/) e [instalación con Docker](https://opentelemetry.io/docs/collector/install/docker/)
- [ ] Repositorios [opentelemetry-collector](https://github.com/open-telemetry/opentelemetry-collector) y [opentelemetry-collector-contrib](https://github.com/open-telemetry/opentelemetry-collector-contrib)
:::

:::step id="repaso" title="Puntos clave para repasar"
- 5 tipos de componentes: receivers, processors, exporters, connectors, extensions.
- Nada se activa hasta aparecer en `service` (pipelines o extensions).
- Pipeline = receivers + processors (opcionales, en orden) + exporters, por señal.
- `memory_limiter` primero; `batch` (o el batching del exporter) al final.
- `validate` antes de desplegar; `${env:VAR}` para secretos y parámetros.
- Escucha en `localhost` por defecto; en contenedores, `0.0.0.0`.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 8](../labs/lab08-collector.labguide.steps.md).
:::
