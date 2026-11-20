---
title: "Laboratorio 3 · Tu primer span y tu primera métrica con el SDK"
description: "Comprueba el comportamiento no-op de la API sin SDK, configura a mano TracerProvider y MeterProvider, crea spans anidados y un contador, y extiende el SDK con un span processor propio."
slug: "lab03-api-sdk"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [lab, api, sdk, python]
duration: "40 minutos"
level: "intermediate"
objectives:
  - "Comprobar que la API sin SDK es no-op."
  - "Configurar el SDK: Resource, TracerProvider, MeterProvider, processors y exporters."
  - "Crear spans anidados, eventos y una métrica personalizada."
  - "Extender el SDK con un span processor propio."
prerequisites:
  - "Laboratorio 2 completado."
links:
  - label: "Sesión 3: material de estudio"
    url: "../estudio/s03-api-sdk.procedure.steps.md"
    icon: "book-open"
    highlight: true
  - label: "Código del laboratorio"
    url: "{{repo_url}}/tree/{{branch}}/labs/lab03-api-sdk"
    icon: "github"
  - label: "Python · Instrumentation (oficial)"
    url: "https://opentelemetry.io/docs/languages/python/instrumentation/"
    icon: "external-link"
---

# {{ title }}

En este laboratorio **no** usas el agente: configuras el SDK en el código. Necesitas dos terminales.

:::step id="noop" title="La API sin SDK"
```bash
cd labs/lab03-api-sdk
python noop_api.py
```

- [ ] La salida muestra `NonRecordingSpan`, `¿Está grabando?: False` y `¿SpanContext válido?: False`.
- [ ] Puedo explicar por qué el código no falló aunque no hay SDK ([Library guidelines](https://opentelemetry.io/docs/specs/otel/library-guidelines/#api-and-minimal-implementation)).
:::

:::step id="leer" title="Leer la configuración del SDK"
Abre `app.py` y ubica sus dos partes:

1. **Configuración del SDK** (una vez): `Resource` con `service.name` y `service.version`; `TracerProvider` con **dos** span processors (`ContadorDeSpans`, escrito por nosotros, y `BatchSpanProcessor(ConsoleSpanExporter())`); `MeterProvider` con un `PeriodicExportingMetricReader` cada 10 s.
2. **Uso de la API**: `trace.get_tracer(...)`, `metrics.get_meter(...)`, el contador `dice.rolls` y los spans `rolldice` → `roll`.

- [ ] Sé qué líneas son del SDK y cuáles de la API.
:::

:::step id="ejecutar" title="Ejecutar y observar"
```bash
flask run -p 8080
```

En la otra terminal: `curl localhost:8080/rolldice` (un par de veces).

- [ ] Aparecen líneas `[ContadorDeSpans] terminó 'roll'` y `terminó 'rolldice'`: los dos processors reciben los mismos spans.
- [ ] El span `roll` tiene `parent_id` igual al `span_id` de `rolldice`, y `rolldice` tiene `parent_id: null`.
- [ ] El span `roll` tiene el evento `lanzando el dado` y el atributo `dice.roll.value`.
- [ ] A los 10 s aparece la métrica `dice.rolls` con un punto por cada valor de `dice.roll.value`, `"is_monotonic": true` y `"aggregation_temporality": 2` (CUMULATIVE).
:::

:::step id="experimentos" title="Experimentos"
Haz cada cambio en `app.py`, reinicia la app (`Ctrl+C` y `flask run -p 8080`) y vuelve a llamar a `/rolldice`.

:::substep id="simple" title="Simple frente a batch"
Cambia `BatchSpanProcessor` por `SimpleSpanProcessor` (impórtalo de `opentelemetry.sdk.trace.export`).

- [ ] Con `SimpleSpanProcessor` cada span se imprime en cuanto termina; con `BatchSpanProcessor` se agrupan (por defecto cada 5000 ms o al llenar un lote de 512).
:::

:::substep id="global" title="Sin provider global"
Comenta la línea `trace.set_tracer_provider(tracer_provider)`.

- [ ] Ya no aparecen spans: `trace.get_tracer` devuelve el tracer no-op de la API porque no hay un provider global registrado.
:::

:::substep id="resource" title="Resource"
Agrega `"deployment.environment.name": "lab"` al `Resource.create(...)`.

- [ ] El nuevo atributo aparece en el `resource` de spans y métricas.
- [ ] Restauré el archivo con `git checkout labs/lab03-api-sdk/app.py`.
:::
:::
