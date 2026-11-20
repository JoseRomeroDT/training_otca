---
title: "Quiz Dominio 1 · Fundamentals of Observability"
description: "14 preguntas sobre observabilidad, señales, OpenTelemetry, instrumentación y convenciones semánticas (18 % del examen). Cada explicación cita la documentación oficial."
slug: "quiz-d1-fundamentos"
type: "test"
version: "1.0.0"
updated: "2026-11-20"
tags: [quiz, dominio-1, otca]
level: "beginner"
passingScore: 75
feedback: "immediate"
shuffle: true
---

# {{ title }}

Umbral: **75 %**, igual que el examen. Después de responder, pulsa **Comprobar** para ver la explicación y su fuente.

:::question id="d1-observabilidad" type="single"
Según el *Observability primer* de OpenTelemetry, ¿qué describe mejor la observabilidad?
- [ ] Tener dashboards con todos los indicadores conocidos del sistema
- [x] Poder entender un sistema desde fuera, haciéndole preguntas sin conocer su funcionamiento interno
- [ ] Recolectar logs de todos los servidores en un solo lugar
- [ ] Medir la disponibilidad de un servicio con pings periódicos
:::explanation
La observabilidad permite entender un sistema desde fuera y resolver problemas nuevos ("unknown unknowns"). Fuente: [Observability primer](https://opentelemetry.io/docs/concepts/observability-primer/).
:::
:::

:::question id="d1-backend" type="true-false" answer="false"
OpenTelemetry es un backend de observabilidad que almacena y visualiza trazas, métricas y logs.
:::explanation
OpenTelemetry genera, exporta y recolecta telemetría; **no es un backend**: el almacenamiento y la visualización quedan, a propósito, en otras herramientas. Fuente: [What is OpenTelemetry?](https://opentelemetry.io/docs/what-is-opentelemetry/)
:::
:::

:::question id="d1-senales" type="multiple"
¿Qué señales **soporta actualmente** OpenTelemetry (no en desarrollo ni en propuesta)? Marca todas.
- [x] Trazas
- [x] Métricas
- [x] Logs
- [x] Baggage
- [ ] Profiles
:::explanation
Hoy: trazas, métricas, logs y baggage. *Events* y *profiles* están en desarrollo o en propuesta. Fuente: [Signals](https://opentelemetry.io/docs/concepts/signals/).
:::
:::

:::question id="d1-historia" type="single"
OpenTelemetry nació de la fusión de dos proyectos. ¿Cuáles?
- [ ] Prometheus y Jaeger
- [x] OpenTracing y OpenCensus
- [ ] Zipkin y OpenMetrics
- [ ] Fluentd y OpenTracing
:::explanation
OpenTelemetry es un proyecto de la CNCF resultado de la fusión de OpenTracing y OpenCensus. Fuente: [What is OpenTelemetry? · History](https://opentelemetry.io/docs/what-is-opentelemetry/#history).
:::
:::

:::question id="d1-slo" type="single"
¿Qué concepto representa la forma de **comunicar la confiabilidad** a la organización, asociando uno o más indicadores a valor de negocio?
- [ ] SLI
- [x] SLO
- [ ] Span
- [ ] Baggage
:::explanation
El SLI es la medición; el SLO comunica la confiabilidad ligando SLIs al valor de negocio. Fuente: [Observability primer · Reliability and metrics](https://opentelemetry.io/docs/concepts/observability-primer/#reliability-and-metrics).
:::
:::

:::question id="d1-match" type="match"
Relaciona cada concepto con su definición oficial:

- Span :: Una unidad de trabajo u operación
- Traza :: El camino de una solicitud a través de varios servicios
- Métrica :: Una medición de un servicio capturada en tiempo de ejecución
- Log :: Un registro de texto con timestamp, estructurado o no
:::explanation
Fuentes: [Observability primer](https://opentelemetry.io/docs/concepts/observability-primer/), [Metrics](https://opentelemetry.io/docs/concepts/signals/metrics/) y [Logs](https://opentelemetry.io/docs/concepts/signals/logs/).
:::
:::

:::question id="d1-root" type="single"
En una traza, ¿cómo se reconoce el *root span*?
- [ ] Es el span con mayor duración
- [x] No tiene ID de span padre
- [ ] Es el único span con estado `Ok`
- [ ] Es el span de tipo `Server`
:::explanation
El root span representa el inicio y fin de la operación completa y no tiene `parent_id`. Fuente: [Traces](https://opentelemetry.io/docs/concepts/signals/traces/).
:::
:::

:::question id="d1-zerocode" type="single"
¿Qué captura típicamente la instrumentación **zero-code**?
- [ ] La lógica de negocio interna de tu aplicación
- [x] Lo que ocurre en los bordes de la aplicación: requests HTTP, llamadas a bases de datos, colas de mensajes
- [ ] Solo las métricas de CPU y memoria del host
- [ ] Nada hasta que se agregan spans manuales
:::explanation
Zero-code instrumenta las librerías que usas (los "bordes"); tu propio código no queda instrumentado. Fuente: [Zero-code](https://opentelemetry.io/docs/concepts/instrumentation/zero-code/).
:::
:::

:::question id="d1-ambas" type="true-false" answer="false"
La instrumentación basada en código y la zero-code no se pueden usar a la vez en la misma aplicación.
:::explanation
La documentación oficial dice explícitamente que se pueden usar ambas simultáneamente. Fuente: [Instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/).
:::
:::

:::question id="d1-service-name" type="single"
Si no configuras `service.name`, ¿qué valor asigna el SDK por defecto?
- [ ] `default`
- [ ] El nombre del host
- [x] `unknown_service`
- [ ] Queda vacío
:::explanation
Los SDK asignan `unknown_service`; por eso se recomienda configurarlo en código o con `OTEL_SERVICE_NAME`. Fuente: [Resources](https://opentelemetry.io/docs/concepts/resources/).
:::
:::

:::question id="d1-semconv-http" type="single"
¿Cuál es el atributo de las convenciones semánticas **estables** para el método de una solicitud HTTP?
- [ ] `http.method`
- [x] `http.request.method`
- [ ] `method`
- [ ] `http.verb`
:::explanation
`http.request.method` es el nombre estable (aparece en la tabla de atributos del primer); `http.method` es el nombre experimental anterior que las instrumentaciones de Python emiten por defecto hasta activar `OTEL_SEMCONV_STABILITY_OPT_IN=http`. Fuentes: [Observability primer](https://opentelemetry.io/docs/concepts/observability-primer/#span-attributes) y [Python · semantic convention stability](https://opentelemetry.io/docs/languages/python/instrumentation/#semantic-convention-stability).
:::
:::

:::question id="d1-libreria-api" type="single"
Estás desarrollando una **librería** que otros usarán y quieres instrumentarla con OpenTelemetry. ¿De qué debes depender?
- [x] Solo de la API de OpenTelemetry
- [ ] De la API y del SDK
- [ ] Solo del SDK
- [ ] Del Collector
:::explanation
Las librerías dependen solo de la API: sin SDK instalado sus llamadas no tienen impacto. Las aplicaciones (procesos ejecutables) dependen de API y SDK. Fuente: [Code-based instrumentation](https://opentelemetry.io/docs/concepts/instrumentation/code-based/).
:::
:::

:::question id="d1-use" type="single"
El método **USE** (*Utilization, Saturation, Errors*) se aplica principalmente a:
- [ ] Las solicitudes de cada servicio
- [x] Los recursos del sistema, como CPU, memoria o disco
- [ ] Los logs de la aplicación
- [ ] El baggage propagado
:::explanation
USE analiza recursos; RED (*Rate, Errors, Duration*) analiza servicios y solicitudes. Fuentes: [The USE Method](https://www.brendangregg.com/usemethod.html) y [span metrics connector (R.E.D.)](https://github.com/open-telemetry/opentelemetry-collector-contrib/tree/main/connector/spanmetricsconnector).
:::
:::

:::question id="d1-bootstrap" type="single"
En Python, ¿qué hace `opentelemetry-bootstrap -a install`?
- [ ] Instala el OpenTelemetry Collector
- [x] Instala las librerías de instrumentación correspondientes a los paquetes que encuentra instalados
- [ ] Ejecuta la aplicación con la auto-instrumentación activada
- [ ] Genera un archivo de configuración YAML
:::explanation
Lee los paquetes de `site-packages` e instala sus instrumentaciones (p. ej., `opentelemetry-instrumentation-flask` si está Flask). La app se ejecuta después con `opentelemetry-instrument`. Fuente: [Python zero-code](https://opentelemetry.io/docs/zero-code/python/).
:::
:::
