---
title: "Sesión 7 · Configuración, OTLP y agentes zero-code"
description: "Configurar el SDK en código, con variables OTEL_* o con un archivo declarativo; el protocolo OTLP (gRPC y HTTP, puertos, rutas, reintentos); y los agentes zero-code. Dominio 2 (46 %)."
slug: "s07-configuracion-otlp"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-2, configuracion, otlp, agentes, zero-code]
level: "intermediate"
objectives:
  - "Configurar el SDK de forma programática y por variables de entorno OTEL_*."
  - "Exportar con OTLP sobre gRPC y sobre HTTP, y diagnosticar combinaciones incorrectas."
  - "Desplegar y configurar un agente zero-code."
  - "Aplicar buenas prácticas de configuración."
links:
  - label: "Laboratorio 7: configuración"
    url: "../labs/lab07-configuracion.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Quiz del Dominio 2"
    url: "../../tests/quiz-d2-api-sdk.test.md"
    icon: "graduation-cap"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 2 · The OpenTelemetry API and SDK (46 %)** — competencias *Configuration* y *Agents*. Cierra el dominio con más peso: al terminar, haz el quiz del Dominio 2.

:::step id="formas" title="Tres formas de configurar el SDK"
1. **En código** (programática): creas providers, processors y exporters tú mismo (labs 3 a 6).
2. **Variables de entorno `OTEL_*`**: comunes a todos los SDK ([SDK configuration](https://opentelemetry.io/docs/languages/sdk-configuration/)). Con el agente de Python, cada opción de línea de comandos tiene su variable: en mayúsculas y con prefijo `OTEL_` (`--service_name` → `OTEL_SERVICE_NAME`) ([agente de Python](https://opentelemetry.io/docs/zero-code/python/configuration/)).
3. **Configuración declarativa**: un archivo YAML indicado con `OTEL_CONFIG_FILE`. El esquema es estable, pero el soporte en los SDK aún es experimental (la página oficial lista Java); con archivo, el SDK ignora las demás variables `OTEL_*` salvo la sustitución `${VAR}` ([Declarative configuration](https://opentelemetry.io/docs/languages/sdk-configuration/declarative-configuration/)).

Variables generales más usadas ([General](https://opentelemetry.io/docs/languages/sdk-configuration/general/) y [especificación](https://opentelemetry.io/docs/specs/otel/configuration/sdk-environment-variables/)):

| Variable | Para qué | Por defecto |
|---|---|---|
| `OTEL_SERVICE_NAME` | `service.name` del Resource | (SDK: `unknown_service`) |
| `OTEL_RESOURCE_ATTRIBUTES` | Otros atributos del Resource, `clave=valor,clave2=valor2` | — |
| `OTEL_TRACES_EXPORTER` / `OTEL_METRICS_EXPORTER` / `OTEL_LOGS_EXPORTER` | Exporter por señal | `otlp` |
| `OTEL_TRACES_SAMPLER` / `OTEL_TRACES_SAMPLER_ARG` | Sampler y su argumento | `parentbased_always_on` |
| `OTEL_PROPAGATORS` | Propagadores | `tracecontext,baggage` |
| `OTEL_METRIC_EXPORT_INTERVAL` | Intervalo de exportación de métricas (ms) | 60000 |
| `OTEL_SDK_DISABLED` | Desactiva el SDK en todas las señales | `false` |
| `OTEL_LOG_LEVEL` | Nivel del logger interno del SDK | `info` |

- [ ] Sé configurar un servicio completo solo con variables de entorno.
:::

:::step id="otlp" title="OTLP: el protocolo de OpenTelemetry"
De la [especificación OTLP](https://opentelemetry.io/docs/specs/otlp/):

- Transportes: **gRPC** (puerto por defecto **4317**) y **HTTP** (puerto por defecto **4318**).
- Codificación del cuerpo: **Protobuf binario** o **JSON Protobuf**.
- Rutas HTTP por defecto: `/v1/traces`, `/v1/metrics` y `/v1/logs`.
- Compresión opcional **gzip**.
- En HTTP se reintentan las respuestas **429, 502, 503 y 504**; el resto de 4xx/5xx no. Un *partial success* no se reintenta.

Variables del exporter ([OTLP exporter](https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/)):

| Variable | Valor por defecto / notas |
|---|---|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | gRPC `http://localhost:4317` · HTTP `http://localhost:4318` (en HTTP el SDK agrega `/v1/traces`, etc.) |
| `OTEL_EXPORTER_OTLP_TRACES_ENDPOINT` (y `_METRICS_`, `_LOGS_`) | Por señal; en HTTP se usa **tal cual**, con la ruta completa |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | `grpc`, `http/protobuf` o `http/json`; el valor por defecto depende del SDK (la especificación recomienda `http/protobuf`) |
| `OTEL_EXPORTER_OTLP_HEADERS` | Cabeceras, p. ej. de autenticación hacia un backend |
| `OTEL_EXPORTER_OTLP_TIMEOUT` | 10000 ms |
| `OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE` | `cumulative` (también `delta` y `lowmemory`) |

> [!WARNING]
> El error clásico es mezclar protocolo y puerto: `grpc` contra el 4318 o `http/protobuf` contra el 4317. En el Lab 7 lo provocarás a propósito y verás `StatusCode.UNAVAILABLE` en los logs de la app.

En Python, la opción `otlp` del agente usa **gRPC** salvo que indiques `http/protobuf` ([agente de Python](https://opentelemetry.io/docs/zero-code/python/configuration/#configuration-properties)).

- [ ] Sé qué puerto y ruta corresponden a cada protocolo.
:::

:::step id="agentes" title="Agentes zero-code"
- Un agente agrega la API y el SDK a la aplicación **sin modificar su código**; el mecanismo depende del lenguaje (manipulación de *bytecode*, *monkey patching*, eBPF). Hay zero-code para .NET, Go, Java, JavaScript, PHP y Python ([Zero-code](https://opentelemetry.io/docs/concepts/instrumentation/zero-code/), [español](https://opentelemetry.io/es/docs/concepts/instrumentation/zero-code/)).
- Se configura con **variables de entorno** y mecanismos propios del lenguaje: fuente de datos, exporters, propagadores y Resource.
- **Python**: `opentelemetry-distro` instala la API, el SDK, `opentelemetry-bootstrap` y `opentelemetry-instrument`; `opentelemetry-bootstrap -a install` instala las instrumentaciones de los paquetes detectados ([Python zero-code](https://opentelemetry.io/docs/zero-code/python/)).
- Opciones útiles de Python: `OTEL_PYTHON_EXCLUDED_URLS` (no instrumentar URLs, p. ej. *health checks*), `OTEL_PYTHON_DISABLED_INSTRUMENTATIONS`, `OTEL_PYTHON_LOG_CORRELATION` ([configuración del agente](https://opentelemetry.io/docs/zero-code/python/configuration/)).
- El agente arma un pipeline que solo se cambia por variables o argumentos; si necesitas más control, configura el SDK en código, y puedes **combinarlo** con instrumentación manual vía la API ([Logs example](https://opentelemetry.io/docs/zero-code/python/logs-example/)).

- [ ] Sé instalar y configurar el agente de Python.
:::

:::step id="practicas" title="Buenas prácticas"
- **Siempre** define `service.name` (y versión y entorno en `OTEL_RESOURCE_ATTRIBUTES`, con convenciones como `deployment.environment.name`).
- Prefiere enviar la telemetría a un **Collector** en vez de directo al backend: simplifica la gestión de secretos, desacopla los problemas de exportación (como los reintentos) de las apps y permite enriquecer los datos ([Operator · auto-instrumentación](https://opentelemetry.io/docs/platforms/kubernetes/operator/automatic/#create-an-opentelemetry-collector-optional)).
- Recuerda que las variables de entorno **tienen prioridad** sobre la configuración en código para los propagadores en Python ([Python · Instrumentation](https://opentelemetry.io/docs/languages/python/instrumentation/#using-environment-variables)).
- Excluye los endpoints de salud y usa el sampler acorde al volumen.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Python · Exporters](https://opentelemetry.io/docs/languages/python/exporters/)
- [ ] [Especificación OTLP](https://opentelemetry.io/docs/specs/otlp/)
- [ ] [SDK configuration](https://opentelemetry.io/docs/languages/sdk-configuration/): [General](https://opentelemetry.io/docs/languages/sdk-configuration/general/) y [OTLP exporter](https://opentelemetry.io/docs/languages/sdk-configuration/otlp-exporter/)
- [ ] [Zero-code (concepto)](https://opentelemetry.io/docs/concepts/instrumentation/zero-code/) y [configuración del agente de Python](https://opentelemetry.io/docs/zero-code/python/configuration/)
- [ ] [Declarative configuration](https://opentelemetry.io/docs/languages/sdk-configuration/declarative-configuration/)
:::

:::step id="repaso" title="Puntos clave para repasar"
- OTLP: gRPC **4317**, HTTP **4318**; rutas `/v1/traces`, `/v1/metrics`, `/v1/logs`.
- Endpoint base en HTTP: el SDK agrega la ruta; endpoint por señal: se usa tal cual.
- `OTEL_*_EXPORTER` por defecto `otlp`; propagadores por defecto `tracecontext,baggage`.
- Reintentos OTLP/HTTP: 429, 502, 503, 504.
- `OTEL_SDK_DISABLED=true` apaga el SDK.
- Agente de Python: `opentelemetry-distro` → `opentelemetry-bootstrap -a install` → `opentelemetry-instrument`.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 7](../labs/lab07-configuracion.labguide.steps.md).
- [ ] Hice el [quiz del Dominio 2](../../tests/quiz-d2-api-sdk.test.md).
:::
