---
title: "Sesión 1 · Introducción a la observabilidad"
description: "Qué es la observabilidad, las señales (trazas, métricas, logs y baggage), qué es y qué no es OpenTelemetry y su lugar en la CNCF. Dominio 1 (18 %)."
slug: "s01-observabilidad"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-1, observabilidad, senales, fundamentos]
duration: "2,5 horas"
level: "beginner"
objectives:
  - "Explicar qué es la observabilidad según la documentación oficial y en qué se diferencia de solo vigilar indicadores conocidos."
  - "Explicar las señales de OpenTelemetry (trazas, métricas, logs y baggage) y el rol de cada una."
  - "Ubicar OpenTelemetry en el ecosistema CNCF: qué es, qué no es y de dónde viene."
  - "Reconocer casos de uso reales con la demo oficial (Astronomy Shop)."
links:
  - label: "Laboratorio 1: Astronomy Shop"
    url: "../labs/lab01-astronomy-shop.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Observability primer"
    url: "https://opentelemetry.io/docs/concepts/observability-primer/"
    icon: "book-open"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 1 · Fundamentals of Observability (18 %)** — competencias *Telemetry Data* y *Analysis and Outcomes*. Lee los conceptos, marca cada lectura oficial y termina con el laboratorio.

:::step id="observabilidad" title="Observabilidad y telemetría"
Según el [Observability primer](https://opentelemetry.io/docs/concepts/observability-primer/) ([en español](https://opentelemetry.io/es/docs/concepts/observability-primer/)):

- **Observabilidad** es poder entender un sistema *desde fuera*, haciéndole preguntas sin conocer su funcionamiento interno. Permite resolver problemas nuevos (los *unknown unknowns*) y responder "¿por qué está pasando esto?".
- Para poder hacer esas preguntas, la aplicación debe estar **instrumentada**: su código emite **señales** (trazas, métricas y logs). Está *bien* instrumentada cuando no hace falta agregar más instrumentación para diagnosticar un problema.
- **Telemetría** son los datos que emite un sistema sobre su comportamiento.
- **Confiabilidad** (*reliability*) responde "¿el servicio hace lo que los usuarios esperan?". Un sistema puede estar arriba el 100 % del tiempo y aun así no ser confiable.
- **SLI** (*Service Level Indicator*): una medición del comportamiento del servicio; una buena SLI lo mide desde la perspectiva del usuario (p. ej., cuánto tarda en cargar una página).
- **SLO** (*Service Level Objective*): la forma de comunicar la confiabilidad a la organización, asociando una o más SLI a valor de negocio.

> [!NOTE]
> La documentación oficial no define "monitoreo". La idea clave para el examen es la de arriba: la observabilidad te deja hacer **preguntas nuevas** a partir de la telemetría, sin tener que agregar código cada vez que aparece un problema distinto.

- [ ] Puedo explicar observabilidad, telemetría, SLI y SLO con mis palabras.
:::

:::step id="senales" title="Las señales"
OpenTelemetry soporta hoy **trazas, métricas, logs y baggage**; *events* (un tipo de log) y *profiles* están en desarrollo o en propuesta ([Signals](https://opentelemetry.io/docs/concepts/signals/)).

| Señal | Qué es | Pregunta que responde |
|---|---|---|
| **Traza** | El camino de una solicitud a través de los servicios: uno o más *spans*; el primero es el *root span* | ¿Por dónde pasó esta solicitud y dónde tardó o falló? |
| **Span** | Una unidad de trabajo u operación, con nombre, tiempos, atributos y eventos | ¿Qué hizo esta operación concreta? |
| **Métrica** | Una medición capturada en tiempo de ejecución; se agrega en el tiempo (tasa de errores, CPU, requests por segundo) | ¿Cuánto, cuántas veces, qué tan rápido, en conjunto? |
| **Log** | Un registro de texto con *timestamp*, estructurado (recomendado) o no | ¿Qué evento puntual ocurrió? |
| **Baggage** | Pares clave-valor que viajan junto al contexto entre servicios | ¿Qué dato de la solicitud necesito más adelante (p. ej., un ID de cliente)? |

Los logs **no** están necesariamente asociados a una solicitud; se vuelven mucho más útiles cuando se **correlacionan** con una traza y un span ([primer](https://opentelemetry.io/docs/concepts/observability-primer/#logs)).

- [ ] Puedo decir qué señal usaría para cada pregunta de la tabla.
:::

:::step id="otel" title="Qué es (y qué no es) OpenTelemetry"
Según [What is OpenTelemetry?](https://opentelemetry.io/docs/what-is-opentelemetry/) ([en español](https://opentelemetry.io/es/docs/what-is-opentelemetry/)):

- Es un **framework y conjunto de herramientas de observabilidad** para **generar, exportar y recolectar** telemetría (trazas, métricas y logs).
- Es **open source** y **agnóstico de proveedor y de herramienta**: funciona con backends open source (Jaeger, Prometheus) y comerciales.
- **No es un backend**: el almacenamiento y la visualización quedan, a propósito, en manos de otras herramientas.
- Dos principios: **los datos que generas son tuyos** (sin *vendor lock-in*) y **aprendes un solo conjunto de APIs y convenciones**.
- Componentes principales: la **especificación**, el protocolo **OTLP**, las **convenciones semánticas**, las **APIs**, los **SDK** por lenguaje, el ecosistema de **librerías de instrumentación**, la **instrumentación automática**, el **Collector** y otras herramientas como el **Operator** de Kubernetes, los **Helm charts** y los recursos para **FaaS**.
- Historia: es un proyecto de la **CNCF** nacido de la **fusión de OpenTracing y OpenCensus**.
- Es **extensible**: receivers propios en el Collector, librerías de instrumentación, distribuciones, exporters y propagadores personalizados.

- [ ] Puedo explicar por qué OpenTelemetry no es un backend y qué piezas lo componen.
:::

:::step id="casos" title="Casos de uso: la demo oficial"
La [OpenTelemetry Demo (Astronomy Shop)](https://opentelemetry.io/docs/demo/) es una tienda de microservicios en varios lenguajes, instrumentada con OpenTelemetry, que trae su propio Collector y backends (Jaeger, Grafana, Prometheus, OpenSearch). Sus *feature flags* simulan problemas reales para practicar el diagnóstico, por ejemplo ([lista oficial](https://opentelemetry.io/docs/demo/feature-flags/)):

- `paymentFailure`: hace fallar un porcentaje de los cobros del servicio de pagos.
- `productCatalogFailure`: provoca errores en `GetProduct` para un producto concreto.
- `recommendationCacheFailure`: genera una fuga de memoria en el servicio de recomendaciones (que está escrito en **Python**).

Con ellos se recorre el ciclo de trabajo de SRE/DevOps: detectar un síntoma en las métricas, ir a las trazas para ver dónde falla y usar los logs correlacionados para ver el detalle. Lo harás en el laboratorio.

- [ ] Sé qué es la demo oficial y para qué sirven sus *feature flags*.
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Observability primer](https://opentelemetry.io/docs/concepts/observability-primer/) · [español](https://opentelemetry.io/es/docs/concepts/observability-primer/)
- [ ] [Signals](https://opentelemetry.io/docs/concepts/signals/) · [español](https://opentelemetry.io/es/docs/concepts/signals/)
- [ ] [What is OpenTelemetry?](https://opentelemetry.io/docs/what-is-opentelemetry/) · [español](https://opentelemetry.io/es/docs/what-is-opentelemetry/)
- [ ] [OpenTelemetry Demo: documentación](https://opentelemetry.io/docs/demo/) y [repositorio](https://github.com/open-telemetry/opentelemetry-demo)
- [ ] (Opcional) Curso gratuito [LFS148: Getting Started with OpenTelemetry](https://training.linuxfoundation.org/training/getting-started-with-opentelemetry-lfs148/)

> [!TIP]
> El examen está en inglés: lee primero la versión en inglés y usa la traducción como apoyo. Las traducciones pueden ir por detrás del original.
:::

:::step id="repaso" title="Puntos clave para repasar"
- La observabilidad requiere **instrumentación**: sin señales no hay preguntas que hacer.
- Señales actuales: **trazas, métricas, logs y baggage**; *profiles* y *events* en desarrollo.
- Una traza se compone de **spans**; el que no tiene padre es el **root span**.
- **OpenTelemetry no almacena ni visualiza** datos: genera, procesa y exporta.
- OpenTelemetry = fusión de **OpenTracing + OpenCensus**, proyecto de la **CNCF**.
- **SLI** mide; **SLO** comunica el objetivo de confiabilidad ligado al negocio.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 1: Astronomy Shop](../labs/lab01-astronomy-shop.labguide.steps.md).
:::
