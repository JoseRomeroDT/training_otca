---
title: "Sesión 9 · Connectors, OTTL y despliegue"
description: "Connectors entre pipelines, transformación de datos con processors y OTTL, y los patrones de despliegue del Collector: sin Collector, agent, gateway y agent → gateway. Dominio 3 (26 %)."
slug: "s09-ottl-despliegue"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-3, connectors, ottl, transform, despliegue]
level: "intermediate"
objectives:
  - "Usar connectors entre pipelines (p. ej. trazas → métricas)."
  - "Transformar, filtrar y enriquecer datos con processors y OTTL."
  - "Comparar los patrones de despliegue agent y gateway."
  - "Diseñar una topología de recolección agent → gateway."
links:
  - label: "Laboratorio 9: OTTL y gateway"
    url: "../labs/lab09-ottl-gateway.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Transforming telemetry"
    url: "https://opentelemetry.io/docs/collector/transforming-telemetry/"
    icon: "book-open"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 3 · The OpenTelemetry Collector (26 %)** — competencias *Transforming Data*, *Deployment* y *Pipelines*.

:::step id="connectors" title="Connectors"
De [Configuration · Connectors](https://opentelemetry.io/docs/collector/configuration/#connectors) y [Components · Connector](https://opentelemetry.io/docs/collector/components/connector/):

- Un **connector une dos pipelines**: consume datos como **exporter** al final de uno y los emite como **receiver** al inicio de otro. Los tipos de datos pueden ser **iguales o distintos**.
- Sirve para **resumir**, **replicar** o **enrutar** datos. Un processor puede modificar o filtrar dentro de un pipeline, pero **no** puede sacar trazas de un pipeline como métricas de otro: para eso está el connector.
- Ejemplos: `count` (cuenta spans, eventos o logs y produce métricas), `span_metrics` (métricas R.E.D. de las trazas: llamadas, errores y duración), `routing` (enruta según condiciones) y `forward` (pasa datos de un pipeline a otro del mismo tipo).
- Como todo componente, configurarlo no lo activa: debe aparecer como **exporter** en un pipeline y como **receiver** en otro.

```yaml
connectors:
  span_metrics: {}
service:
  pipelines:
    traces:
      receivers: [otlp]
      exporters: [otlp_grpc/jaeger, span_metrics]   # sale de aquí…
    metrics:
      receivers: [otlp, span_metrics]               # …y entra aquí
      exporters: [prometheus]
```

- [ ] Sé explicar qué hace un connector que no puede hacer un processor.
:::

:::step id="transformar" title="Transformar telemetría con processors"
De [Transforming telemetry](https://opentelemetry.io/docs/collector/transforming-telemetry/): el Collector es un buen lugar para transformar datos por **calidad, gobierno, costo y seguridad** (las transformaciones complejas impactan el rendimiento).

| Necesidad | Processor |
|---|---|
| Filtrar (descartar lo que cumple una condición) | `filter` (con OTTL) |
| Agregar, actualizar o borrar atributos de spans, logs o métricas | `attributes` |
| Lo mismo, pero en atributos del **Resource** | `resource` |
| Renombrar métricas o etiquetas | `metricstransform` |
| Agregar metadatos del host o la nube | `resource_detection` |
| Agregar metadatos de Kubernetes | `k8s_attributes` |
| Transformaciones avanzadas en las tres señales | `transform` (con OTTL) |
| Muestreo | `probabilistic_sampler`, `tail_sampling` |

Del [troubleshooting](https://opentelemetry.io/docs/collector/troubleshooting/#collector-is-not-processing-data): el processor `attributes` trabaja solo sobre los atributos (*tags*) de los spans; el **nombre** del span lo maneja el processor `span`.
:::

:::step id="ottl" title="OTTL: OpenTelemetry Transformation Language"
OTTL es el lenguaje que usan `transform`, `filter` y otros componentes ([OTTL](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/pkg/ottl), [transform processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/transformprocessor)).

- Una **sentencia** es una función con argumentos y, opcionalmente, una condición `where`: `set(span.attributes["lab.sesion"], "09") where span.name == "roll"`.
- Las **rutas** (*paths*) empiezan por el contexto: `resource`, `scope`, `span`, `spanevent`, `metric`, `datapoint`, `log`… (p. ej., `span.attributes["x"]`, `log.body`, `resource.attributes["service.name"]`).
- Funciones que modifican datos (*editors*): `set`, `delete_key`, `keep_keys`, `replace_pattern`, `truncate_all`, `limit`… Funciones que devuelven valores (*converters*): `SHA256`, `IsMatch`, `Concat`…
- `error_mode`: `ignore` (registra el error y sigue; **recomendado**), `silent` (sigue sin registrar) o `propagate` (devuelve el error y **se descarta el lote**).

```yaml
processors:
  transform:
    error_mode: ignore
    trace_statements:
      - set(span.attributes["player.name"], SHA256(span.attributes["player.name"])) where span.attributes["player.name"] != nil
    log_statements:
      - set(log.severity_text, "FAIL") where log.body == "request failed"
  filter/solo-warn:
    error_mode: ignore
    log_conditions:
      - log.severity_number < SEVERITY_NUMBER_WARN   # lo que cumple, se DESCARTA
```

> [!NOTE]
> En el Collector v0.165 el processor `filter` usa `trace_conditions`, `metric_conditions` y `log_conditions` con rutas con prefijo. El formato anterior (`traces: span:` / `logs: log_record:`), que todavía aparece en algunas páginas, está *deprecated* ([filter processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/filterprocessor)).

- [ ] Puedo leer una sentencia OTTL y decir qué hace.
:::

:::step id="despliegue" title="Patrones de despliegue"
De [Deployment](https://opentelemetry.io/docs/collector/deploy/):

| Patrón | Cómo es | A favor | En contra |
|---|---|---|---|
| **Sin Collector** | Las apps exportan directo al backend | Simple (desarrollo y pruebas); nada más que operar | Cambiar la recolección requiere tocar código; acopla la app al backend; pocos exporters por lenguaje |
| **Agent** | Un Collector junto a la app o en el mismo host (*sidecar* o DaemonSet) | Fácil de empezar; relación 1 a 1 clara app ↔ Collector | Escalabilidad limitada; poco flexible para despliegues complejos |
| **Gateway** | Uno o más Collectors como servicio independiente detrás de un endpoint OTLP (por clúster, centro de datos o región) | Credenciales y políticas centralizadas (filtrado, sampling) | Una pieza más que puede fallar; más latencia si se encadenan; más recursos |

Fuentes: [no-collector](https://opentelemetry.io/docs/collector/deploy/other/no-collector/), [agent](https://opentelemetry.io/docs/collector/deploy/agent/), [gateway](https://opentelemetry.io/docs/collector/deploy/gateway/).

**Agent → gateway** ([guía oficial](https://opentelemetry.io/docs/collector/deploy/other/agent-to-gateway/)):

- Ambos llevan `memory_limiter` primero y batching: lotes **pequeños** en los agents, **grandes** en los gateways.
- El **tail sampling** va **solo en los gateways** (debe ver todos los spans de una traza); en los agents se usa el `loadbalancing` exporter para enviar cada traza, por Trace ID, a la misma instancia del gateway.
- Con varios Collectors, cada flujo de métricas debe tener un **único escritor** (*single-writer*); si no, aparecen huecos, saltos o errores como `out-of-order samples` en Prometheus.

- [ ] Sé qué patrón elegir según el caso y dónde va el tail sampling.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Transforming telemetry](https://opentelemetry.io/docs/collector/transforming-telemetry/)
- [ ] [Connectors](https://opentelemetry.io/docs/collector/configuration/#connectors) y [Components · Connector](https://opentelemetry.io/docs/collector/components/connector/) · [español](https://opentelemetry.io/es/docs/collector/components/connector/)
- [ ] [OTTL (README)](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/pkg/ottl) y [transform processor](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/processor/transformprocessor)
- [ ] [Deployment](https://opentelemetry.io/docs/collector/deploy/), [agent](https://opentelemetry.io/docs/collector/deploy/agent/), [gateway](https://opentelemetry.io/docs/collector/deploy/gateway/) y [agent-to-gateway](https://opentelemetry.io/docs/collector/deploy/other/agent-to-gateway/)
:::

:::step id="repaso" title="Puntos clave para repasar"
- Connector = exporter de un pipeline + receiver de otro; puede cambiar el tipo de señal.
- `span_metrics` genera métricas R.E.D. a partir de spans.
- OTTL: rutas con contexto (`span.`, `log.`, `resource.`…), funciones y `where`; `error_mode: ignore` recomendado.
- `filter` descarta lo que cumple la condición.
- Gateway: políticas y credenciales centralizadas; agent: simple y 1 a 1.
- Tail sampling solo en gateways, con `loadbalancing` por Trace ID en los agents.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 9](../labs/lab09-ottl-gateway.labguide.steps.md).
:::
