---
title: "Laboratorio 0 · Tu entorno en GitHub Codespaces"
description: "Crea el Codespace del curso, levanta el entorno de laboratorio (Collector + Jaeger + Prometheus) y comprueba que la telemetría llega con una prueba de humo."
slug: "lab00-codespaces"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [lab, codespaces, entorno]
duration: "20 minutos"
level: "beginner"
objectives:
  - "Crear un Codespace a partir del repositorio del curso."
  - "Levantar el entorno de laboratorio y abrir Jaeger y Prometheus."
  - "Enviar un span, una métrica y un log de prueba y encontrarlos."
prerequisites:
  - "Una cuenta de GitHub con acceso a Codespaces."
  - "Un navegador moderno (todo se hace en la nube)."
links:
  - label: "Abrir el Codespace"
    url: "https://codespaces.new/{{owner}}/{{repo_name}}?quickstart=1"
    icon: "flask-conical"
    highlight: true
  - label: "Entorno de laboratorio (código)"
    url: "{{repo_url}}/tree/{{branch}}/labs/lab-env"
    icon: "github"
  - label: "Documentación de GitHub Codespaces"
    url: "https://docs.github.com/en/codespaces/about-codespaces/what-are-codespaces"
    icon: "book-open"
---

# {{ title }}

El Codespace es una máquina Linux en la nube con VS Code en el navegador. Ya trae Python 3.12 con las librerías de OpenTelemetry, Docker, `kubectl`, Helm y `kind`. Todos los laboratorios se hacen ahí.

```text
apps de los labs ──OTLP──▶ otel-collector ──▶ Jaeger      (trazas)      :16686
(localhost:4317/4318)                    ──▶ Prometheus  (métricas)    :9090
                                         ──▶ debug       (logs, en la consola del Collector)
```

:::step id="crear" title="Crear el Codespace"
1. Pulsa **Abrir el Codespace** (arriba) o, en el repositorio, **Code → Codespaces → Create codespace on main**.
2. La primera vez tarda unos minutos: construye la imagen y ejecuta `.devcontainer/post-create.sh` (entorno Python, `kind` e imágenes de Docker).
3. Para los laboratorios 1 y 10 conviene una máquina de **4 núcleos**. Para elegirla: **Code → Codespaces → … → New with options… → Machine type** ([tipos de máquina](https://docs.github.com/en/codespaces/customizing-your-codespace/changing-the-machine-type-for-your-codespace)).

> [!TIP]
> Con `?quickstart=1`, si ya tienes un Codespace de este repositorio, GitHub te ofrece reabrirlo en vez de crear otro.

- [ ] El Codespace abrió VS Code en el navegador.
- [ ] En la terminal aparece "Codespace listo" (o el prompt con `(.venv)`).
:::

:::step id="verificar" title="Verificar las herramientas"
Abre una **terminal nueva** (menú ☰ → Terminal → New Terminal) y ejecuta:

```bash
python --version
pip list 2>/dev/null | grep -i opentelemetry-sdk
docker version --format '{{.Server.Version}}'
kubectl version --client
kind version
```

- [ ] `python` es 3.12 y aparece `opentelemetry-sdk 1.45.2`.
- [ ] Docker, `kubectl` y `kind` responden sin errores.
:::

:::step id="levantar" title="Levantar el entorno de laboratorio"
```bash
labs/lab-env/up.sh
```

El script copia la configuración inicial del Collector a `labs/lab-env/active/`, levanta los contenedores y comprueba que respondan.

- [ ] La salida muestra `OK` para el Collector, Jaeger y Prometheus.
- [ ] En la pestaña **PORTS** de VS Code aparecen los puertos 16686 (Jaeger UI) y 9090 (Prometheus).
- [ ] Abrí Jaeger con el icono del globo 🌐 del puerto 16686.
:::

:::step id="humo" title="Prueba de humo: un span, una métrica y un log"
```bash
python labs/lab-env/smoke_test.py
```

- [ ] En **Jaeger**: en *Service* elige `smoke-test` y pulsa **Find Traces**; aparece la traza `prueba-de-humo`.
- [ ] En **Prometheus** (puerto 9090): consulta `smoke_runs_total` y aparece con valor 1 (el exporter del Collector la expone durante 5 minutos sin nuevas mediciones).
- [ ] En el **Collector**: `docker logs otel-collector 2>&1 | grep -i "prueba de humo"` muestra el log, y cerca aparecen su `Trace ID` y `Span ID`.

> [!NOTE]
> Fíjate en que el log trae el **mismo Trace ID** que imprimió el script: la correlación log ↔ traza que estudiarás en la Sesión 6.
:::

:::step id="apagar" title="Apagar y ahorrar cuota"
- `labs/lab-env/down.sh` detiene los contenedores (la configuración activa se conserva).
- Al terminar el día, **detén el Codespace** (Code → Codespaces → … → Stop codespace). Los Codespaces consumen cuota mientras están encendidos ([facturación de Codespaces](https://docs.github.com/en/billing/concepts/product-billing/github-codespaces)).

- [ ] Sé apagar el entorno y el Codespace.
:::
