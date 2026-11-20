---
title: "Laboratorio 11 · Depurar pipelines rotos"
description: "Cuatro escenarios con fallas reales: una configuración inválida, un Collector que arranca pero no entrega, un error de protocolo en la app y una propagación rota. Usa validate, logs, zPages, métricas internas y el debug exporter. Cierra con una prueba de resiliencia."
slug: "lab11-depuracion"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [lab, depuracion, troubleshooting, zpages, resiliencia]
duration: "60 minutos"
level: "advanced"
objectives:
  - "Detectar errores de configuración con otelcol-contrib validate."
  - "Diagnosticar un pipeline que arranca pero no entrega datos."
  - "Diagnosticar fallas de exportación y de propagación de contexto."
  - "Observar la cola de envío y los reintentos del Collector ante una caída del backend."
prerequisites:
  - "Laboratorios 6, 7 y 8 completados."
  - "Entorno levantado (labs/lab-env/up.sh)."
links:
  - label: "Sesión 11: material de estudio"
    url: "../estudio/s11-depuracion.procedure.steps.md"
    icon: "book-open"
    highlight: true
  - label: "Código del laboratorio"
    url: "{{repo_url}}/tree/{{branch}}/labs/lab11-depuracion"
    icon: "github"
  - label: "Collector · Troubleshooting (oficial)"
    url: "https://opentelemetry.io/docs/collector/troubleshooting/"
    icon: "external-link"
---

# {{ title }}

Intenta diagnosticar cada escenario **antes** de mirar su solución. Herramientas: `otelcol-contrib validate`, `docker logs`, zPages (puerto 55679), métricas internas en Prometheus (`otelcol_*`) y el exporter `debug`.

:::step id="a" title="Escenario A · Una configuración que no arranca"
```bash
labs/lab-env/use-collector-config.sh labs/lab11-depuracion/escenario-a.yaml
```

- [ ] `validate` rechazó la configuración y el script **no** la activó (el Collector siguió con la anterior).
- [ ] Encontré en el mensaje qué componente referencia el pipeline que no está definido.
- [ ] Lo comparé con `escenario-a-solucion.yaml` (`diff labs/lab11-depuracion/escenario-a*.yaml`).

> [!TIP]
> `validate` detecta errores de **estructura** (componentes inexistentes, tipos o campos mal escritos), no de **operación** (un endpoint al que no se llega). Para esos está el escenario B.
:::

:::step id="b" title="Escenario B · Arranca, pero no entrega"
```bash
labs/lab-env/use-collector-config.sh labs/lab11-depuracion/escenario-b.yaml
```

Genera tráfico con el Lab 4 (gRPC) y con el Lab 7 (HTTP):

```bash
# Terminal 1 (gRPC → localhost:4317)
cd labs/lab04-trazas && python dice_server.py
# Terminal 2 (gRPC → localhost:4317)
cd labs/lab04-trazas && LAB_PARTIDAS=3 python player.py
# Terminal 3 (HTTP → localhost:4318), en el puerto 8081 para no chocar con el Lab 4
cd labs/lab07-configuracion && source otel.env
export OTEL_EXPORTER_OTLP_PROTOCOL=http/protobuf OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318
opentelemetry-instrument flask run -p 8081
# Terminal 2 otra vez
curl -s "localhost:8081/rolldice?player=ana"; echo
```

Investiga con estas preguntas (el [checklist oficial](https://opentelemetry.io/docs/collector/troubleshooting/#checklist-for-debugging-complex-pipelines)):

1. ¿La app logra **enviar**? Mira la terminal de `player.py` y de `dice_server.py`.
2. ¿En qué dirección **escucha** el receiver? `docker logs otel-collector 2>&1 | grep -i "endpoint"`.
3. ¿Qué pipelines y exporters hay **activos**? Abre zPages → `/debug/pipelinez`.
4. ¿Qué **acepta** y qué **envía** el Collector? En Prometheus: `otelcol_receiver_accepted_spans` y `otelcol_exporter_sent_spans` (por etiqueta `exporter`).

- [ ] Encontré por qué las apps por **gRPC** reciben `StatusCode.UNAVAILABLE` mientras que por **HTTP** sí llegan datos.
- [ ] Encontré por qué no hay trazas en Jaeger aunque el debug exporter sí las muestra.
- [ ] Encontré por qué no hay métricas `dice_*` en Prometheus.
- [ ] Activé `escenario-b-solucion.yaml` y todo volvió a fluir. Leí sus comentarios.
:::

:::step id="c" title="Escenario C · La app exporta al lugar equivocado"
Repite el error del Lab 7 y, esta vez, explícalo con la especificación:

```bash
cd labs/lab07-configuracion && source otel.env
OTEL_EXPORTER_OTLP_ENDPOINT=http://localhost:4318 opentelemetry-instrument flask run -p 8080
```

- [ ] Los logs de la app muestran `StatusCode.UNAVAILABLE` hacia `localhost:4318`: gRPC espera el puerto **4317**; el **4318** es OTLP/HTTP ([OTLP](https://opentelemetry.io/docs/specs/otlp/)).
- [ ] La app sigue respondiendo: el SDK registra el error en lugar de lanzar una excepción ([Error handling](https://opentelemetry.io/docs/specs/otel/error-handling/)).
:::

:::step id="d" title="Escenario D · La traza partida"
Con los servicios del Lab 6, rompe la propagación (`LAB_PROPAGAR=0 python frontend.py`) y diagnostica **solo con la telemetría**, como si no conocieras el código:

- [ ] En Jaeger, una misma solicitud aparece como dos trazas y el span del backend no tiene padre.
- [ ] En los logs del Collector, los logs del frontend y del backend tienen Trace ID distintos.
- [ ] Concluí que el header `traceparent` no viajó (o no se leyó) y lo comprobé en la respuesta (`traceparent_recibido: null`).
:::

:::step id="resiliencia" title="Resiliencia: el backend se cae"
Con la configuración del curso (`labs/lab-env/reset-collector.sh`) y los servicios del Lab 4 corriendo:

```bash
docker stop jaeger
cd labs/lab04-trazas && LAB_PARTIDAS=20 python player.py
docker logs otel-collector 2>&1 | grep -i -m3 "retry"
```

En Prometheus, consulta `otelcol_exporter_queue_size` y `otelcol_exporter_send_failed_spans`. Después:

```bash
docker start jaeger
```

- [ ] Mientras Jaeger estaba caído, el exporter `otlp_grpc/jaeger` **reintentó** y la cola de envío creció.
- [ ] Al volver Jaeger, la cola se vació y las trazas de esas partidas **aparecieron** en Jaeger: `retry_on_failure` + `sending_queue` evitaron la pérdida ([Resiliency](https://opentelemetry.io/docs/collector/resiliency/)). (Las trazas de **antes** de la caída ya no están: este Jaeger guarda en memoria y se reinició.)
- [ ] Sé que si la caída hubiera durado más que `max_elapsed_time` (300 s por defecto) o la cola se hubiera llenado, esos datos se habrían perdido.
:::

:::step id="cerrar" title="Cerrar"
```bash
cd "$(git rev-parse --show-toplevel)" && labs/lab-env/reset-collector.sh
```

- [ ] Volví a la configuración del curso y detuve los servicios de prueba.
:::
