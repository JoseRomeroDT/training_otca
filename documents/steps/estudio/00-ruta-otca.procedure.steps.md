---
title: "Ruta OTCA: sílabo y avance del curso"
description: "Las 12 sesiones (25 h) del entrenamiento para la certificación OpenTelemetry Certified Associate, alineadas con los 4 dominios oficiales del examen. Marca cada sesión, laboratorio y quiz para ver tu avance."
slug: "ruta-otca"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [otca, silabo, ruta, opentelemetry, certificacion]
duration: "25 horas académicas"
level: "beginner"
objectives:
  - "Conocer el formato oficial del examen OTCA y el peso de cada dominio."
  - "Seguir las 12 sesiones del curso: material de estudio, laboratorio y quiz."
  - "Llegar al examen habiendo practicado con simulacros tipo OTCA."
prerequisites:
  - "Cuenta de GitHub (los laboratorios se hacen en GitHub Codespaces, en el navegador)."
  - "Python básico y uso básico de una terminal."
  - "Nociones de contenedores y YAML (se repasan en los laboratorios)."
links:
  - label: "Abrir el entorno de laboratorio (Codespaces)"
    url: "https://codespaces.new/{{owner}}/{{repo_name}}?quickstart=1"
    icon: "flask-conical"
    highlight: true
  - label: "Examen OTCA (Linux Foundation)"
    url: "https://training.linuxfoundation.org/certification/opentelemetry-certified-associate-otca/"
    icon: "graduation-cap"
  - label: "Currículo oficial (CNCF, PDF)"
    url: "https://github.com/cncf/curriculum/blob/main/OTCA_Curriculum.pdf"
    icon: "book-open"
  - label: "Repositorio del curso"
    url: "{{repo_url}}"
    icon: "github"
---

# {{ title }}

Esta es la ruta completa del entrenamiento. Cada sesión tiene tres piezas: **material de estudio** (con lecturas de la documentación oficial), un **laboratorio** práctico en GitHub Codespaces y, por dominio, un **quiz** tipo examen. Marca cada casilla al terminarla: el avance se guarda **en este navegador** (si cambias de equipo o de navegador, empiezas de cero).

> [!TIP]
> Empieza por el [Laboratorio 0](../labs/lab00-codespaces.labguide.steps.md): deja listo tu Codespace en 10 minutos y lo reutilizas en todo el curso.

:::step id="examen" title="El examen OTCA en datos oficiales"
| Dato | Valor oficial |
|---|---|
| Formato | En línea, supervisado (*proctored*), opción múltiple |
| Preguntas | 60 |
| Duración | 90 minutos |
| Puntaje para aprobar | 75 % |
| Costo | USD 250, incluye un reintento |
| Plazo para rendirlo | 12 meses desde la compra |
| Vigencia de la certificación | 2 años |
| Prerrequisitos | Ninguno |
| Idioma de las preguntas | Inglés (los términos técnicos del curso se dejan en inglés por eso) |

Fuentes: [página del examen en Linux Foundation](https://training.linuxfoundation.org/certification/opentelemetry-certified-associate-otca/), [página de CNCF](https://www.cncf.io/training/certification/otca/), [FAQ de exámenes de opción múltiple](https://docs.linuxfoundation.org/tc-docs/certification/faq-mc) (75 % y 90 min) [instrucciones de exámenes de opción múltiple](https://docs.linuxfoundation.org/tc-docs/certification/important-instructions-mc) (60 preguntas) y [idiomas disponibles por examen](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2/language) (OTCA: solo inglés).

**Dominios y peso** (iguales en la página de Linux Foundation, la de CNCF y el [PDF del currículo](https://github.com/cncf/curriculum/blob/main/OTCA_Curriculum.pdf)):

| Dominio | Peso | Competencias |
|---|---|---|
| 1. Fundamentals of Observability | 18 % | Telemetry Data · Semantic Conventions · Instrumentation · Analysis and Outcomes |
| 2. The OpenTelemetry API and SDK | 46 % | Data Model · Composability and Extension · Configuration · Signals (Tracing, Metric, Log) · SDK Pipelines · Context Propagation · Agents |
| 3. The OpenTelemetry Collector | 26 % | Configuration · Deployment · Scaling · Pipelines · Transforming Data |
| 4. Maintaining and Debugging Observability Pipelines | 10 % | Context Propagation · Debugging Pipelines · Error Handling · Schema Management |

> [!NOTE]
> El archivo [`otca/README.md`](https://github.com/cncf/curriculum/tree/main/otca) del repositorio de CNCF muestra otra tabla (cinco dominios de 20 %). Las páginas oficiales del examen y el PDF del currículo coinciden en la tabla de arriba, que es la que usa este curso.

- [ ] Leí cómo es el examen y el peso de cada dominio.
:::

:::step id="plan" title="Plan de las 12 sesiones"
| Sesión | Horas | Dominio | Tema | Laboratorio |
|---|---|---|---|---|
| 1 | 2,5 | 1 | Introducción a la observabilidad | Astronomy Shop (demo oficial) |
| 2 | 2,5 | 1 | Instrumentación y convenciones semánticas | Zero-code en Python |
| 3 | 2 | 2 | API vs SDK y modelo de datos | Primer span y primera métrica con el SDK |
| 4 | 2 | 2 | Trazas: spans, processors y sampling | Trazado distribuido de 2 servicios |
| 5 | 2 | 2 | Métricas: instrumentos y agregación | Métricas de negocio por OTLP |
| 6 | 2 | 2 | Logs, contexto y propagación | Logs correlacionados y propagación W3C |
| 7 | 2 | 2 | Configuración, OTLP y agentes zero-code | Configuración solo con variables `OTEL_*` |
| 8 | 2 | 3 | Collector: componentes y pipelines | Tu propio Collector con las 3 señales |
| 9 | 2 | 3 | Connectors, OTTL y despliegue | OTTL + patrón agent → gateway |
| 10 | 2 | 3 | Operator, Kubernetes y escalamiento | Operator en kind + auto-instrumentación |
| 11 | 2 | 4 | Mantenimiento y depuración de pipelines | Depurar pipelines rotos |
| 12 | 2 | Todos | Repaso integral y simulacro | Simulacros tipo examen |

Todos los laboratorios usan **Python** y una misma app de dados (`dice-server`) que evoluciona sesión a sesión; en las sesiones de Collector y Kubernetes la configuración es YAML.

- [ ] Revisé el plan del curso.
:::

:::step id="s01" title="Sesión 1 · Introducción a la observabilidad"
- [ ] Estudié la [Sesión 1](s01-observabilidad.procedure.steps.md).
- [ ] Hice el [Laboratorio 0: Codespaces](../labs/lab00-codespaces.labguide.steps.md).
- [ ] Hice el [Laboratorio 1: Astronomy Shop](../labs/lab01-astronomy-shop.labguide.steps.md).
:::

:::step id="s02" title="Sesión 2 · Instrumentación y convenciones semánticas"
- [ ] Estudié la [Sesión 2](s02-instrumentacion-semconv.procedure.steps.md).
- [ ] Hice el [Laboratorio 2: zero-code](../labs/lab02-zero-code.labguide.steps.md).
- [ ] Aprobé el [quiz del Dominio 1](../../tests/quiz-d1-fundamentos.test.md).
:::

:::step id="s03" title="Sesión 3 · API vs SDK y modelo de datos"
- [ ] Estudié la [Sesión 3](s03-api-sdk.procedure.steps.md).
- [ ] Hice el [Laboratorio 3: API y SDK](../labs/lab03-api-sdk.labguide.steps.md).
:::

:::step id="s04" title="Sesión 4 · Trazas: spans, processors y sampling"
- [ ] Estudié la [Sesión 4](s04-trazas.procedure.steps.md).
- [ ] Hice el [Laboratorio 4: trazas](../labs/lab04-trazas.labguide.steps.md).
:::

:::step id="s05" title="Sesión 5 · Métricas: instrumentos y agregación"
- [ ] Estudié la [Sesión 5](s05-metricas.procedure.steps.md).
- [ ] Hice el [Laboratorio 5: métricas](../labs/lab05-metricas.labguide.steps.md).
:::

:::step id="s06" title="Sesión 6 · Logs, contexto y propagación"
- [ ] Estudié la [Sesión 6](s06-logs-contexto.procedure.steps.md).
- [ ] Hice el [Laboratorio 6: logs y contexto](../labs/lab06-logs-contexto.labguide.steps.md).
:::

:::step id="s07" title="Sesión 7 · Configuración, OTLP y agentes zero-code"
- [ ] Estudié la [Sesión 7](s07-configuracion-otlp.procedure.steps.md).
- [ ] Hice el [Laboratorio 7: configuración](../labs/lab07-configuracion.labguide.steps.md).
- [ ] Aprobé el [quiz del Dominio 2](../../tests/quiz-d2-api-sdk.test.md).
:::

:::step id="s08" title="Sesión 8 · Collector: componentes y pipelines"
- [ ] Estudié la [Sesión 8](s08-collector.procedure.steps.md).
- [ ] Hice el [Laboratorio 8: tu Collector](../labs/lab08-collector.labguide.steps.md).
:::

:::step id="s09" title="Sesión 9 · Connectors, OTTL y despliegue"
- [ ] Estudié la [Sesión 9](s09-ottl-despliegue.procedure.steps.md).
- [ ] Hice el [Laboratorio 9: OTTL y gateway](../labs/lab09-ottl-gateway.labguide.steps.md).
:::

:::step id="s10" title="Sesión 10 · Operator, Kubernetes y escalamiento"
- [ ] Estudié la [Sesión 10](s10-kubernetes-operator.procedure.steps.md).
- [ ] Hice el [Laboratorio 10: Kubernetes](../labs/lab10-kubernetes.labguide.steps.md).
- [ ] Aprobé el [quiz del Dominio 3](../../tests/quiz-d3-collector.test.md).
:::

:::step id="s11" title="Sesión 11 · Mantenimiento y depuración"
- [ ] Estudié la [Sesión 11](s11-depuracion.procedure.steps.md).
- [ ] Hice el [Laboratorio 11: depuración](../labs/lab11-depuracion.labguide.steps.md).
- [ ] Aprobé el [quiz del Dominio 4](../../tests/quiz-d4-depuracion.test.md).
:::

:::step id="s12" title="Sesión 12 · Repaso integral y simulacro"
- [ ] Estudié la [Sesión 12](s12-repaso-simulacro.procedure.steps.md).
- [ ] Hice el [simulacro OTCA](../../tests/otca-simulacro-01.test.md) y obtuve 80 % o más.
- [ ] Repasé los temas de las preguntas que fallé.
:::

:::step id="certificacion" title="A rendir el examen"
- [ ] Compré el examen en [Linux Foundation](https://training.linuxfoundation.org/certification/opentelemetry-certified-associate-otca/) y lo agendé.
- [ ] Leí las [instrucciones oficiales](https://docs.linuxfoundation.org/tc-docs/certification/important-instructions-mc) del día del examen.
:::
