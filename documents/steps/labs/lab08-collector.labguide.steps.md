---
title: "Laboratorio 8 · Tu propio Collector con las tres señales"
description: "Construye paso a paso la configuración de un Collector: receiver OTLP, exporters a Jaeger, Prometheus y debug, processors en el orden correcto, extensiones de diagnóstico y telemetría interna; valídala y actívala en cada paso."
slug: "lab08-collector"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [lab, collector, pipelines, yaml]
level: "intermediate"
objectives:
  - "Escribir una configuración del Collector y validarla con otelcol-contrib validate."
  - "Construir pipelines de trazas, métricas y logs."
  - "Ordenar processors (memory_limiter, resource, batch) y activar extensiones."
  - "Enrutar cada señal a su backend."
prerequisites:
  - "Laboratorio 7 completado."
  - "Entorno levantado (labs/lab-env/up.sh)."
links:
  - label: "Sesión 8: material de estudio"
    url: "../estudio/s08-collector.procedure.steps.md"
    icon: "book-open"
    highlight: true
  - label: "Código del laboratorio"
    url: "{{repo_url}}/tree/{{branch}}/labs/lab08-collector"
    icon: "github"
  - label: "Collector · Configuration (oficial)"
    url: "https://opentelemetry.io/docs/collector/configuration/"
    icon: "external-link"
---

# {{ title }}

Hasta ahora el Collector del curso era una caja negra. Aquí escribes el tuyo desde cero. En cada paso usarás:

```bash
labs/lab-env/use-collector-config.sh labs/lab08-collector/mi-collector.yaml
```

Ese script ejecuta `otelcol-contrib validate` (con la imagen 0.165.0) y, si la configuración es válida, la activa y reinicia el contenedor `otel-collector`. Para generar telemetría de prueba usa `python labs/lab-env/smoke_test.py` o los servicios del Lab 4.

:::step id="minimo" title="El Collector mínimo"
```bash
cp labs/lab08-collector/inicio.yaml labs/lab08-collector/mi-collector.yaml
labs/lab-env/use-collector-config.sh labs/lab08-collector/mi-collector.yaml
python labs/lab-env/smoke_test.py
docker logs otel-collector 2>&1 | tail -5
```

`inicio.yaml` tiene un receiver (`otlp`), un exporter (`debug`) y un pipeline de `traces`.

- [ ] `validate` no dio errores y el contenedor arrancó.
- [ ] En los logs del Collector aparece una línea `Traces` con la cantidad de spans recibidos.
- [ ] La métrica y el log de la prueba de humo **no** se procesaron (en el log del smoke test o del Collector verás que no hay pipeline de `metrics` ni de `logs`). Y Jaeger no recibió nada: no hay exporter hacia él.
:::

:::step id="jaeger" title="Exportar trazas a Jaeger"
Agrega el exporter y súmalo al pipeline de `traces`:

```yaml
exporters:
  debug:
    verbosity: basic
  otlp_grpc/jaeger:
    endpoint: jaeger:4317
    tls:
      insecure: true

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp_grpc/jaeger, debug]
```

Valida, activa y vuelve a enviar la prueba de humo.

- [ ] La traza `prueba-de-humo` aparece en Jaeger.
- [ ] Entiendo el identificador `tipo/nombre`: `otlp_grpc` es el tipo y `jaeger` el nombre.
:::

:::step id="senales" title="Pipelines de métricas y logs"
```yaml
exporters:
  # … los anteriores, más:
  debug/detallado:
    verbosity: detailed
  prometheus:
    endpoint: 0.0.0.0:8889

service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp_grpc/jaeger, debug]
    metrics:
      receivers: [otlp]
      exporters: [prometheus]
    logs:
      receivers: [otlp]
      exporters: [debug/detallado]
```

- [ ] Prometheus muestra `smoke_runs_total` (lo lee del exporter `prometheus` en `otel-collector:8889`).
- [ ] `docker logs otel-collector 2>&1 | grep -A8 "LogRecord"` muestra el log con su `Trace ID`.
- [ ] El mismo receiver `otlp` alimenta los tres pipelines (se crea una sola instancia que reparte los datos).
:::

:::step id="processors" title="Processors en el orden correcto"
```yaml
processors:
  memory_limiter:
    check_interval: 1s
    limit_percentage: 75
    spike_limit_percentage: 15
  resource/lab:
    attributes:
      - key: deployment.environment.name
        value: lab
        action: upsert
  batch: {}
```

Y en **cada** pipeline: `processors: [memory_limiter, resource/lab, batch]`.

- [ ] En Jaeger, el Process de las trazas nuevas incluye `deployment.environment.name=lab`.
- [ ] Sé por qué `memory_limiter` va primero y `batch` al final ([recomendados](https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/README.md#recommended-processors)).
:::

:::step id="extensiones" title="Extensiones y telemetría interna"
```yaml
extensions:
  health_check:
    endpoint: 0.0.0.0:13133
  zpages:
    endpoint: 0.0.0.0:55679
  pprof:
    endpoint: 0.0.0.0:1777

service:
  extensions: [health_check, zpages, pprof]
  telemetry:
    metrics:
      readers:
        - pull:
            exporter:
              prometheus:
                host: 0.0.0.0
                port: 8888
  pipelines:
    # … los tres pipelines
```

- [ ] `labs/lab-env/status.sh` vuelve a mostrar `OK` para el health check.
- [ ] En zPages (puerto 55679) abrí `/debug/pipelinez` y vi mis tres pipelines con sus componentes.
- [ ] En Prometheus consulté `otelcol_receiver_accepted_spans` y `otelcol_exporter_sent_spans` (métricas internas; desde v0.152 no llevan el sufijo `_total`).
:::

:::step id="comparar" title="Comparar con la solución y explorar"
```bash
diff labs/lab08-collector/mi-collector.yaml labs/lab08-collector/solucion.yaml
docker run --rm otel/opentelemetry-collector-contrib:0.165.0 components | head -60
```

- [ ] Mi configuración hace lo mismo que `solucion.yaml`.
- [ ] Con `components` vi los receivers, processors, exporters, connectors y extensiones de la distribución contrib y su estabilidad.
- [ ] (Experimento) Definí un exporter sin agregarlo a ningún pipeline: `validate` lo acepta, pero no se usa. **Configurar no es activar.**
- [ ] Volví a la configuración del curso con `labs/lab-env/reset-collector.sh`.
:::
