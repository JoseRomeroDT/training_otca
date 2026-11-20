---
title: "Quiz Dominio 4 · Maintaining and Debugging Observability Pipelines"
description: "12 preguntas sobre fallas de propagación, herramientas de depuración del Collector, manejo de errores, resiliencia y telemetry schemas (10 % del examen). Cada explicación cita la documentación oficial."
slug: "quiz-d4-depuracion"
type: "test"
version: "1.0.0"
updated: "2026-11-20"
tags: [quiz, dominio-4, otca, depuracion]
duration: "15 minutos"
level: "advanced"
passingScore: 75
feedback: "immediate"
shuffle: true
---

# {{ title }}

Umbral: **75 %**.

:::question id="d4-traza-partida" type="single"
Una sola solicitud entre dos servicios aparece en el backend como **dos trazas distintas**. ¿Cuál es la causa más probable?
- [ ] El sampler del segundo servicio es `AlwaysOn`
- [x] El contexto no se propagó: el emisor no inyectó el header o el receptor no lo extrajo
- [ ] El Collector usa el processor `batch`
- [ ] Los dos servicios tienen el mismo `service.name`
:::explanation
Sin inject en el emisor o extract en el receptor, el segundo servicio crea una traza nueva. Fuente: [Context propagation](https://opentelemetry.io/docs/concepts/context-propagation/).
:::
:::

:::question id="d4-debug" type="single"
¿Cuál es la verbosidad por defecto del exporter `debug`?
- [x] `basic`
- [ ] `normal`
- [ ] `detailed`
- [ ] `silent`
:::explanation
`basic` (resumen); `normal` y `detailed` muestran más contenido. Fuente: [debug exporter](https://github.com/open-telemetry/opentelemetry-collector/blob/main/exporter/debugexporter/README.md).
:::
:::

:::question id="d4-zpages" type="single"
¿Qué extensión del Collector expone en el puerto 55679 la página `/debug/tracez` para ver latencias, errores y spans que no terminan?
- [ ] `pprof`
- [ ] `health_check`
- [x] `zpages`
- [ ] `file_storage`
:::explanation
zPages inspecciona datos en vivo de receivers y exporters; `/debug/tracez` sirve para latencias, deadlocks y errores. Fuente: [Collector · Troubleshooting · zPages](https://opentelemetry.io/docs/collector/troubleshooting/#zpages).
:::
:::

:::question id="d4-puertos" type="match"
Relaciona cada herramienta de diagnóstico del Collector con su puerto por defecto:

- Métricas internas (Prometheus) :: 8888
- zPages :: 55679
- pprof :: 1777
- health_check :: 13133
:::explanation
Fuentes: [Internal telemetry](https://opentelemetry.io/docs/collector/internal-telemetry/) y [Collector · Configuration](https://opentelemetry.io/docs/collector/configuration/).
:::
:::

:::question id="d4-no-recibe" type="single"
El Collector arranca sin errores pero no recibe datos de un receiver que sí está configurado en la sección `receivers`. ¿Qué causa menciona la documentación?
- [ ] El receiver tiene un nombre con `/`
- [x] El receiver está definido pero no está habilitado en ningún pipeline
- [ ] Falta la extensión `pprof`
- [ ] El processor `batch` está al final
:::explanation
Entre las causas de "no recibe datos": red, configuración del receiver o del cliente, y un receiver definido pero no habilitado en ningún pipeline. Fuente: [Collector · Troubleshooting · Collector is not receiving data](https://opentelemetry.io/docs/collector/troubleshooting/#collector-is-not-receiving-data).
:::
:::

:::question id="d4-span-name" type="single"
Quieres cambiar el **nombre** de los spans en el Collector, pero el processor `attributes` no lo hace. ¿Por qué?
- [ ] El nombre del span no se puede cambiar en el Collector
- [x] `attributes` trabaja solo sobre los atributos (tags) del span; el nombre lo maneja el processor `span`
- [ ] Falta `error_mode: propagate`
- [ ] El processor `attributes` solo funciona con métricas
:::explanation
Fuente: [Collector · Troubleshooting · Collector is not processing data](https://opentelemetry.io/docs/collector/troubleshooting/#collector-is-not-processing-data).
:::
:::

:::question id="d4-excepciones" type="true-false" answer="false"
Si el exporter de un SDK no puede conectarse con el Collector, el SDK lanza una excepción que detiene la aplicación en tiempo de ejecución.
:::explanation
Las implementaciones no deben lanzar excepciones no controladas en tiempo de ejecución; los errores suprimidos deberían registrarse. Solo pueden fallar rápido al iniciar (p. ej., por configuración inválida). Fuente: [Error handling](https://opentelemetry.io/docs/specs/otel/error-handling/).
:::
:::

:::question id="d4-retry" type="number" answer="300"
¿Cuántos segundos dura por defecto `max_elapsed_time` de `retry_on_failure` en los exporters del Collector (tiempo máximo reintentando un lote)?
:::explanation
300 s, con `initial_interval` 5 s, `max_interval` 30 s y `multiplier` 1,5. Fuente: [exporterhelper · Retry on Failure](https://github.com/open-telemetry/opentelemetry-collector/blob/main/exporter/exporterhelper/README.md#retry-on-failure).
:::
:::

:::question id="d4-perdida" type="multiple"
¿En qué situaciones puede perder datos el Collector según la guía de resiliencia? Marca todas.
- [x] El destino está caído más tiempo que `max_elapsed_time`
- [x] La cola de envío se llena antes de que el destino se recupere
- [x] El Collector se cae y solo usaba una cola en memoria
- [ ] El exporter usa una cola persistente con `file_storage` y el Collector se reinicia normalmente
:::explanation
Con cola persistente, lo encolado se retoma al reiniciar. Fuente: [Resiliency · Circumstances of data loss](https://opentelemetry.io/docs/collector/resiliency/#circumstances-of-data-loss).
:::
:::

:::question id="d4-schema" type="single"
¿Para qué sirve el **schema URL** en la telemetría?
- [ ] Para autenticar el envío hacia el backend
- [x] Para identificar la versión del telemetry schema con que se emitieron los datos y poder transformarlos entre versiones
- [ ] Para indicar la URL del Collector
- [ ] Para comprimir los datos con gzip
:::explanation
Los schemas están versionados, definen transformaciones entre versiones y se identifican con un Schema URL que termina en la versión. Fuente: [Telemetry Schemas](https://opentelemetry.io/docs/specs/otel/schemas/).
:::
:::

:::question id="d4-schema-otlp" type="single"
¿Dónde transporta OTLP el `schema_url`?
- [ ] En un header HTTP aparte
- [x] En los mensajes de nivel Resource (ResourceSpans, ResourceMetrics, ResourceLogs) y de nivel Instrumentation Scope
- [ ] Solo en cada atributo de span
- [ ] OTLP no transporta el schema URL
:::explanation
Fuente: [Telemetry Schemas · OTLP Support](https://opentelemetry.io/docs/specs/otel/schemas/#otlp-support).
:::
:::

:::question id="d4-checklist" type="multiple"
Según el checklist oficial para depurar pipelines complejos, ¿qué conviene verificar en **cada salto**? Marca todas las que aparecen en la lista.
- [x] Si hay mensajes de error en los logs del Collector
- [x] Cómo se modifica la telemetría en ese componente (por ejemplo, sampling o redacción)
- [x] Cómo está configurado el siguiente salto
- [x] Si hay políticas de red que impidan la entrada o salida de datos
- [ ] El número de dashboards del backend
:::explanation
Fuente: [Collector · Troubleshooting · Checklist for debugging complex pipelines](https://opentelemetry.io/docs/collector/troubleshooting/#checklist-for-debugging-complex-pipelines).
:::
:::
