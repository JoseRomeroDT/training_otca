---
title: "Laboratorio 1 · Astronomy Shop: las tres señales en acción"
description: "Despliega la demo oficial de OpenTelemetry en tu Codespace, recorre trazas, métricas y logs de una tienda de microservicios y diagnostica una falla simulada con un feature flag."
slug: "lab01-astronomy-shop"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [lab, demo, astronomy-shop, senales]
level: "beginner"
objectives:
  - "Desplegar la OpenTelemetry Demo (Astronomy Shop) con Docker Compose."
  - "Identificar trazas, métricas y logs de una aplicación real de microservicios."
  - "Provocar una falla con un feature flag y encontrarla con la telemetría."
prerequisites:
  - "Laboratorio 0 completado."
  - "Codespace de 4 núcleos recomendado (el modo mínimo necesita unos 3 GB de RAM y el completo unos 6 GB)."
links:
  - label: "Sesión 1: material de estudio"
    url: "../estudio/s01-observabilidad.procedure.steps.md"
    icon: "book-open"
    highlight: true
  - label: "Demo: despliegue con Docker"
    url: "https://opentelemetry.io/docs/demo/docker-deployment/"
    icon: "external-link"
  - label: "Demo: feature flags"
    url: "https://opentelemetry.io/docs/demo/feature-flags/"
    icon: "external-link"
---

# {{ title }}

La [OpenTelemetry Demo](https://opentelemetry.io/docs/demo/) es una tienda en línea hecha con más de diez microservicios en distintos lenguajes, todos instrumentados con OpenTelemetry, con su propio Collector, Jaeger, Prometheus, Grafana y OpenSearch. Usaremos la versión **3.1.0**.

:::step id="preparar" title="Liberar puertos y clonar la demo"
La demo publica los puertos 8080 y 9090, que también usa el entorno del curso. Apágalo primero:

```bash
labs/lab-env/down.sh
cd ~
git clone --depth 1 --branch 3.1.0 https://github.com/open-telemetry/opentelemetry-demo.git
cd opentelemetry-demo
```

- [ ] El entorno del curso está detenido (`docker ps` no muestra `otel-collector`).
- [ ] Clonaste la demo fuera de la carpeta del curso.
:::

:::step id="levantar" title="Levantar la demo"
Según la memoria de tu Codespace ([modos de despliegue](https://opentelemetry.io/docs/demo/docker-deployment/#deployment-modes)):

```bash
make start-minimal   # sin Kafka ni sus servicios: ~3 GB (recomendado con 2 núcleos)
# o bien
make start           # demo completa: ~6 GB (recomendado con 4 núcleos)
```

La primera vez descarga muchas imágenes y tarda varios minutos. Revisa el estado con:

```bash
docker ps --format 'table {{.Names}}\t{{.Status}}' | head -40
```

- [ ] Los contenedores están en estado `Up`.
:::

:::step id="tienda" title="Recorrer la tienda"
En la pestaña **PORTS**, abre el puerto **8080** con el globo 🌐. Desde esa URL ([rutas oficiales](https://opentelemetry.io/docs/demo/docker-deployment/#verify-the-web-store-and-telemetry)):

| Ruta | Qué es |
|---|---|
| `/` | La tienda |
| `/loadgen/` | Generador de carga (ya envía tráfico sintético) |
| `/feature` | Configurador de feature flags |
| `/jaeger/ui/` | Jaeger (trazas) |
| `/grafana/` | Grafana (métricas, y logs vía OpenSearch) |

- [ ] Agregué un producto al carrito y completé una compra en la tienda.
:::

:::step id="trazas" title="Trazas en Jaeger"
1. Abre `/jaeger/ui/`. En *Service* elige `frontend` y pulsa **Find Traces**.
2. Abre una traza con muchos spans (p. ej., una que incluya `checkout`).

- [ ] Encontré una traza que pasa por varios servicios (`frontend`, `checkout`, `payment`, `shipping`…).
- [ ] Identifiqué el **root span**, spans hijos y spans de tipo `client` y `server` en distintos servicios.
- [ ] En un span, revisé sus **atributos** (p. ej., `http.*`, `rpc.*`) y los del **Process/Resource** (`service.name`, `telemetry.sdk.language`).
:::

:::step id="metricas-logs" title="Métricas y logs en Grafana"
Abre `/grafana/` → **Dashboards**. La demo trae, entre otros, *Demo Dashboard*, *Spanmetrics Demo Dashboard*, *OpenTelemetry Collector* y *APM Dashboard (Jaeger, Prometheus, OpenSearch)*.

- [ ] En *Spanmetrics Demo Dashboard* vi tasas de llamadas, errores y duraciones por servicio (métricas RED generadas a partir de las trazas).
- [ ] En **Explore**, con el datasource **OpenSearch**, encontré logs de los servicios.
- [ ] Encontré al menos un log que incluye el ID de traza y el ID de span (correlación con trazas).
:::

:::step id="falla" title="Diagnosticar una falla simulada"
1. Abre `/feature`, busca **`paymentFailure`** y cámbialo a `50%` (vista básica). Guarda. Este flag hace fallar ese porcentaje de los cobros del servicio `payment` ([lista oficial de flags](https://opentelemetry.io/docs/demo/feature-flags/)).
2. Espera uno o dos minutos con el generador de carga funcionando.
3. En Jaeger, busca trazas del servicio `payment` con el tag `error=true`.

- [ ] En Grafana subió la tasa de errores del servicio `payment`.
- [ ] En Jaeger encontré una traza con el span de `payment` en estado **Error** y su evento de excepción.
- [ ] Devolví `paymentFailure` a `off`.

> [!TIP]
> Este es el ciclo que repetirás en todo el curso: **métricas** para detectar el síntoma, **trazas** para ubicar dónde falla y **logs** correlacionados para el detalle.
:::

:::step id="apagar" title="Apagar la demo y volver al entorno del curso"
```bash
cd ~/opentelemetry-demo && make stop
cd /workspaces/$(basename "$GITHUB_REPOSITORY") && labs/lab-env/up.sh
```

- [ ] La demo está detenida y el entorno del curso volvió a estar `OK`.
:::
