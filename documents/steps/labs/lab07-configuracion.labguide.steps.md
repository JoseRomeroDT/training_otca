---
title: "Laboratorio 7 · Configuración solo con variables OTEL_*"
description: "Configura una app sin código de OpenTelemetry únicamente con variables de entorno y el agente zero-code; cambia entre OTLP gRPC y HTTP, provoca un error de protocolo y apaga el SDK."
slug: "lab07-configuracion"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [lab, configuracion, otlp, zero-code]
level: "intermediate"
objectives:
  - "Configurar Resource, exporters, sampler y propagadores con variables OTEL_*."
  - "Exportar con OTLP sobre gRPC (4317) y sobre HTTP/protobuf (4318)."
  - "Reconocer el error de mezclar protocolo y puerto."
  - "Excluir URLs y desactivar el SDK sin tocar el código."
prerequisites:
  - "Laboratorio 6 completado."
  - "Entorno levantado (labs/lab-env/up.sh)."
links:
  - label: "Sesión 7: material de estudio"
    url: "../estudio/s07-configuracion-otlp.procedure.steps.md"
    icon: "book-open"
    highlight: true
  - label: "Código del laboratorio"
    url: "{{repo_url}}/tree/{{branch}}/labs/lab07-configuracion"
    icon: "github"
  - label: "SDK configuration (oficial)"
    url: "https://opentelemetry.io/docs/languages/sdk-configuration/"
    icon: "external-link"
---

# {{ title }}

`app.py` no tiene código de OpenTelemetry y `otel.env` contiene toda la configuración. Cada `export` vale para la terminal donde lo ejecutas: si algo queda raro, abre una terminal nueva.

:::step id="leer" title="Leer la configuración"
```bash
cd labs/lab07-configuracion
cat otel.env
```

- [ ] Identifico en `otel.env`: nombre del servicio, atributos del Resource, exporters por señal, protocolo y endpoint OTLP, sampler, propagadores, intervalo de métricas y la exclusión de `/health`.
:::

:::step id="grpc" title="Ejecutar con OTLP gRPC"
```bash
source otel.env
opentelemetry-instrument flask run -p 8080
```

En otra terminal:

```bash
for i in 1 2 3; do curl -s "localhost:8080/rolldice?player=ana"; echo; done
curl -s localhost:8080/health; echo
```

- [ ] En Jaeger, el servicio `dice-server` tiene trazas `GET /rolldice` y en **Process** aparecen `service.version=2.0.0` y `deployment.environment.name=lab`.
- [ ] **No** hay trazas de `/health` (`OTEL_PYTHON_EXCLUDED_URLS=health`).
- [ ] En Prometheus aparecen métricas que empiezan por `http_server` (generadas por la instrumentación de Flask).
:::

:::step id="http" title="Cambiar a OTLP HTTP/protobuf"
Detén la app y, en la misma terminal:

```bash
export OTEL_EXPORTER_OTLP_PROTOCOL="http/protobuf"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
opentelemetry-instrument flask run -p 8080
```

- [ ] Las trazas siguen llegando a Jaeger: con HTTP el SDK agrega `/v1/traces`, `/v1/metrics` y `/v1/logs` al endpoint base.
:::

:::step id="error" title="Provocar un error de protocolo"
Detén la app y mezcla protocolo y puerto:

```bash
export OTEL_EXPORTER_OTLP_PROTOCOL="grpc"
export OTEL_EXPORTER_OTLP_ENDPOINT="http://localhost:4318"
opentelemetry-instrument flask run -p 8080
```

Envía algunas solicitudes y espera unos segundos.

- [ ] En la terminal de la app aparecen mensajes como `Transient error StatusCode.UNAVAILABLE encountered while exporting traces to localhost:4318`.
- [ ] La app **sigue respondiendo**: el SDK no lanza excepciones por fallas de exportación, las registra ([Error handling](https://opentelemetry.io/docs/specs/otel/error-handling/)).
- [ ] Lo corregí con `source otel.env`.
:::

:::step id="variables" title="Más variables para probar"
Prueba cada una (detén la app, exporta la variable, vuelve a ejecutar y luego `source otel.env`):

| Variable | Qué deberías ver |
|---|---|
| `export OTEL_TRACES_SAMPLER_ARG="0.2"` | Aproximadamente 1 de cada 5 requests aparece en Jaeger |
| `export OTEL_SEMCONV_STABILITY_OPT_IN="http"` | Atributos estables (`http.request.method`, `url.path`…) en los spans |
| `export OTEL_SDK_DISABLED="true"` | Nada llega al Collector: el SDK queda desactivado |
| `export OTEL_PROPAGATORS="b3"` | La app **no arranca**: `ValueError: Propagator b3 not found. It is either misspelled or not installed.` (falta `opentelemetry-propagator-b3`). Es un fallo **al iniciar** por configuración inválida, que la especificación permite; en tiempo de ejecución, en cambio, el SDK no debe lanzar excepciones |

- [ ] Probé al menos tres variables y volví a `source otel.env`.
- [ ] Detuve la app.
:::
