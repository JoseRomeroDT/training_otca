---
title: "Quiz Dominio 3 · The OpenTelemetry Collector"
description: "16 preguntas sobre configuración, pipelines, transformación con OTTL, connectors, despliegue, Operator y escalamiento del Collector (26 % del examen). Cada explicación cita la documentación oficial."
slug: "quiz-d3-collector"
type: "test"
version: "1.0.0"
updated: "2026-11-20"
tags: [quiz, dominio-3, otca, collector]
duration: "20 minutos"
level: "intermediate"
passingScore: 75
feedback: "immediate"
shuffle: true
---

# {{ title }}

Umbral: **75 %**. Los nombres de componentes siguen la versión 0.165.0 del Collector (`otlp_grpc`, `otlp_http`, `span_metrics`…).

:::question id="d3-activar" type="true-false" answer="false"
Definir un exporter en la sección `exporters` de la configuración es suficiente para que el Collector lo use.
:::explanation
Configurar un componente no lo activa: receivers, processors, exporters y connectors se activan al incluirlos en `service.pipelines` (las extensions, en `service.extensions`). Fuente: [Collector · Configuration](https://opentelemetry.io/docs/collector/configuration/).
:::
:::

:::question id="d3-pipeline" type="multiple"
¿Qué tipos de componentes se listan **dentro de un pipeline** en `service.pipelines`? Marca todos.
- [x] receivers
- [x] processors
- [x] exporters
- [ ] extensions
:::explanation
Un pipeline tiene receivers, processors (opcionales) y exporters; los connectors aparecen como exporter de un pipeline y receiver de otro. Las extensions se activan en `service.extensions`. Fuente: [Collector · Configuration · Service](https://opentelemetry.io/docs/collector/configuration/#service).
:::
:::

:::question id="d3-orden" type="order"
Ordena los processors de un pipeline según la recomendación oficial:

1. memory_limiter
2. Processors de sampling o filtrado
3. Processors de transformación o enriquecimiento
4. batch
:::explanation
`memory_limiter` primero; luego lo que descarta datos; después lo que transforma; `batch` al final (y hoy se recomienda preferir el batching del exporter cuando esté disponible). Fuente: [Recommended processors](https://github.com/open-telemetry/opentelemetry-collector/blob/main/processor/README.md#recommended-processors).
:::
:::

:::question id="d3-connector" type="single"
¿Qué hace un **connector**?
- [ ] Conecta el Collector con un backend comercial
- [x] Une dos pipelines: es exporter al final de uno y receiver al inicio de otro
- [ ] Une dos Collectors por la red
- [ ] Reemplaza al receiver OTLP
:::explanation
Un connector consume como exporter de un pipeline y emite como receiver de otro, y el tipo de datos puede cambiar (p. ej. trazas → métricas). Fuente: [Collector · Configuration · Connectors](https://opentelemetry.io/docs/collector/configuration/#connectors).
:::
:::

:::question id="d3-red" type="single"
Quieres obtener métricas de llamadas, errores y duración (R.E.D.) a partir de las trazas que ya pasan por el Collector. ¿Qué componente usas?
- [ ] El processor `batch`
- [x] El connector `span_metrics`
- [ ] El exporter `prometheus`
- [ ] El receiver `host_metrics`
:::explanation
`span_metrics` agrega métricas R.E.D. a partir de los spans. Fuente: [span metrics connector](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector).
:::
:::

:::question id="d3-validate" type="single"
¿Cómo validas un archivo de configuración del Collector antes de desplegarlo?
- [ ] `otelcol check --file=config.yaml`
- [x] `otelcol validate --config=config.yaml`
- [ ] `otelcol --dry-run config.yaml`
- [ ] No se puede validar sin arrancarlo
:::explanation
El subcomando `validate` revisa la configuración. Fuente: [Collector · Configuration · Location](https://opentelemetry.io/docs/collector/configuration/#location).
:::
:::

:::question id="d3-env" type="single"
¿Qué sintaxis usa la configuración del Collector para leer una variable de entorno, con un valor por defecto si no existe?
- [ ] `$DB_KEY || mydefault`
- [ ] `{{ env "DB_KEY" "mydefault" }}`
- [x] `${env:DB_KEY:-mydefault}`
- [ ] `%DB_KEY%`
:::explanation
Fuente: [Collector · Configuration · Environment variables](https://opentelemetry.io/docs/collector/configuration/#environment-variables).
:::
:::

:::question id="d3-localhost" type="single"
Un Collector corre en un contenedor con el receiver OTLP configurado en `localhost:4317` y el puerto publicado. Las apps de fuera del contenedor no logran enviarle datos por gRPC. ¿Por qué?
- [ ] gRPC no se puede usar en contenedores
- [x] `localhost` dentro del contenedor solo acepta conexiones de su propia interfaz; hay que escuchar en `0.0.0.0`
- [ ] Falta agregar el receiver a un pipeline de métricas
- [ ] El puerto de OTLP/gRPC es 4318
:::explanation
El Collector usa `localhost` por defecto (por seguridad); en contenedores los ejemplos oficiales usan `0.0.0.0`. Fuente: [Collector · Configuration](https://opentelemetry.io/docs/collector/configuration/#basics).
:::
:::

:::question id="d3-error-mode" type="single"
En el transform processor (OTTL), ¿qué `error_mode` recomienda la documentación?
- [x] `ignore`: registra el error y sigue con la siguiente sentencia
- [ ] `propagate`: devuelve el error y descarta el lote
- [ ] `silent`: sigue sin registrar nada
- [ ] `strict`: detiene el Collector
:::explanation
`ignore` es el recomendado; `propagate` hace que se descarte el payload; `silent` no registra. Fuente: [transform processor · General Config](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/transformprocessor#general-config).
:::
:::

:::question id="d3-filter" type="single"
En el filter processor, ¿qué pasa con la telemetría que **cumple** alguna de las condiciones?
- [ ] Es la única que se conserva
- [x] Se descarta
- [ ] Se marca con un atributo
- [ ] Se envía a un pipeline de errores
:::explanation
La telemetría que cumple cualquiera de las condiciones se descarta. Fuente: [Transforming telemetry · Basic filtering](https://opentelemetry.io/docs/collector/transforming-telemetry/#basic-filtering).
:::
:::

:::question id="d3-patrones" type="match"
Relaciona cada patrón de despliegue con una ventaja que le atribuye la documentación oficial:

- Sin Collector :: No hay piezas adicionales que desplegar ni operar
- Agent :: Relación uno a uno clara entre aplicación y Collector
- Gateway :: Credenciales y políticas gestionadas de forma central
:::explanation
Fuentes: [no-collector](https://opentelemetry.io/docs/collector/deploy/other/no-collector/), [agent](https://opentelemetry.io/docs/collector/deploy/agent/) y [gateway](https://opentelemetry.io/docs/collector/deploy/gateway/).
:::
:::

:::question id="d3-tail" type="single"
En una arquitectura agent → gateway, ¿dónde va el **tail sampling**?
- [ ] En los agents, para descartar datos lo antes posible
- [x] Solo en los gateways, con el exporter `loadbalancing` en los agents para enviar cada traza a la misma instancia
- [ ] En el SDK de cada aplicación
- [ ] En cualquier Collector, da igual
:::explanation
El tail sampling necesita ver todos los spans de una traza; por eso va en los gateways, con balanceo por Trace ID desde los agents. Fuente: [Agent-to-gateway · Sampling considerations](https://opentelemetry.io/docs/collector/deploy/other/agent-to-gateway/#sampling-considerations).
:::
:::

:::question id="d3-fanout" type="single"
El mismo receiver aparece en tres pipelines. ¿Cuántas instancias del receiver crea el Collector?
- [x] Una sola, que reparte los datos a los pipelines (fan-out)
- [ ] Tres, una por pipeline
- [ ] Ninguna: un receiver no puede repetirse
- [ ] Depende del número de exporters
:::explanation
Se crea una sola instancia que envía los datos a un *fan-out consumer*; en cambio, un processor repetido crea una instancia por pipeline. Fuente: [Collector · Architecture](https://opentelemetry.io/docs/collector/architecture/).
:::
:::

:::question id="d3-operator-orden" type="single"
Con el OpenTelemetry Operator, ¿qué debe existir **antes** de desplegar un pod con la anotación `instrumentation.opentelemetry.io/inject-python: "true"`?
- [ ] Un HorizontalPodAutoscaler
- [x] Un recurso `Instrumentation` en el namespace
- [ ] Un sidecar con el Collector
- [ ] Un ConfigMap con el código de la app
:::explanation
Si el recurso `Instrumentation` no existe cuando arranca el pod, el init container de auto-instrumentación no se crea. Fuente: [Operator · Troubleshooting · Were the resources deployed in the right order?](https://opentelemetry.io/docs/platforms/kubernetes/operator/automatic/#were-the-resources-deployed-in-the-right-order).
:::
:::

:::question id="d3-python-operator" type="single"
La auto-instrumentación de **Python** inyectada por el Operator exporta por OTLP usando:
- [ ] gRPC al puerto 4317
- [x] HTTP/protobuf, por eso el endpoint apunta al puerto 4318
- [ ] JSON sobre HTTP al puerto 4317
- [ ] El protocolo de Jaeger
:::explanation
Para Python, el Instrumentation usa `http/protobuf` (gRPC no está soportado). Fuente: [Injecting auto-instrumentation · Python](https://opentelemetry.io/docs/platforms/kubernetes/operator/automatic/#python).
:::
:::

:::question id="d3-escalar" type="single"
Según la guía de escalamiento, ¿cuándo conviene considerar escalar el Collector a partir de su cola de envío?
- [ ] Cuando `otelcol_exporter_queue_size` llega al 100 % de la capacidad
- [x] Cuando `otelcol_exporter_queue_size` llega al 60-70 % de `otelcol_exporter_queue_capacity`
- [ ] Nunca: la cola se ajusta sola
- [ ] Cuando aumenta `otelcol_exporter_send_failed_spans`
:::explanation
La guía sugiere escalar al 60-70 % de la capacidad de la cola. Un aumento de `send_failed` indica fallas permanentes hacia el backend: ahí escalar el Collector suele empeorar las cosas. Fuente: [Scaling the Collector · When to scale](https://opentelemetry.io/docs/collector/scaling/#when-to-scale).
:::
:::
