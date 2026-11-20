---
title: "Sesión 12 · Repaso integral y simulacro"
description: "Cómo prepararse para el día del examen, repaso por dominio con enlaces a cada sesión, y práctica con los quizzes por dominio y el simulacro tipo OTCA para identificar zonas débiles."
slug: "s12-repaso-simulacro"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [repaso, simulacro, examen, otca]
duration: "2 horas"
level: "advanced"
objectives:
  - "Resolver preguntas tipo examen de los cuatro dominios."
  - "Identificar las zonas débiles y volver a la sesión correspondiente."
  - "Llegar al examen conociendo su formato y reglas."
links:
  - label: "Simulacro OTCA"
    url: "../../tests/otca-simulacro-01.test.md"
    icon: "graduation-cap"
    highlight: true
  - label: "Currículo oficial (PDF)"
    url: "https://github.com/cncf/curriculum/blob/main/OTCA_Curriculum.pdf"
    icon: "book-open"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

Última sesión: practica con preguntas tipo examen, mide tu resultado por dominio y vuelve a la sesión que necesites.

:::step id="formato" title="El examen en números"
Datos oficiales ([Linux Foundation](https://training.linuxfoundation.org/certification/opentelemetry-certified-associate-otca/), [FAQ](https://docs.linuxfoundation.org/tc-docs/certification/faq-mc), [instrucciones](https://docs.linuxfoundation.org/tc-docs/certification/important-instructions-mc)): **60 preguntas** de opción múltiple, **90 minutos**, aprobación con **75 %**, en línea y supervisado; resultados por correo en un máximo de 24 horas.

Cuentas útiles (estimaciones propias a partir de esos datos, no cifras oficiales):

- 90 min ÷ 60 preguntas = **1,5 minutos por pregunta**.
- 75 % de 60 = **45 respuestas correctas** como mínimo.
- Preguntas esperables por dominio según su peso: Dominio 1 ≈ 11, Dominio 2 ≈ 28, Dominio 3 ≈ 16, Dominio 4 ≈ 6.

> [!IMPORTANT]
> El Dominio 2 (API y SDK) vale casi la mitad del examen. Si tienes que priorizar el repaso, empieza por ahí.

- [ ] Conozco el formato y las reglas del examen.
:::

:::step id="repaso-dominios" title="Repaso por dominio"
| Dominio | Peso | Sesiones | Quiz |
|---|---|---|---|
| 1. Fundamentals of Observability | 18 % | [S1](s01-observabilidad.procedure.steps.md) · [S2](s02-instrumentacion-semconv.procedure.steps.md) | [Quiz D1](../../tests/quiz-d1-fundamentos.test.md) |
| 2. The OpenTelemetry API and SDK | 46 % | [S3](s03-api-sdk.procedure.steps.md) · [S4](s04-trazas.procedure.steps.md) · [S5](s05-metricas.procedure.steps.md) · [S6](s06-logs-contexto.procedure.steps.md) · [S7](s07-configuracion-otlp.procedure.steps.md) | [Quiz D2](../../tests/quiz-d2-api-sdk.test.md) |
| 3. The OpenTelemetry Collector | 26 % | [S8](s08-collector.procedure.steps.md) · [S9](s09-ottl-despliegue.procedure.steps.md) · [S10](s10-kubernetes-operator.procedure.steps.md) | [Quiz D3](../../tests/quiz-d3-collector.test.md) |
| 4. Maintaining and Debugging Observability Pipelines | 10 % | [S11](s11-depuracion.procedure.steps.md) | [Quiz D4](../../tests/quiz-d4-depuracion.test.md) |

- [ ] Repasé los "Puntos clave" de las 11 sesiones.
:::

:::step id="practica" title="Práctica tipo examen"
1. Haz los **cuatro quizzes por dominio** y anota el porcentaje de cada uno.
2. Haz el [**simulacro OTCA**](../../tests/otca-simulacro-01.test.md) de un tirón, con cronómetro. Apunta a **80 % o más** (por encima del 75 % del examen, como margen).
3. En cada pregunta fallada, lee la explicación y vuelve a la sesión del dominio correspondiente.
4. Repite el quiz del dominio más débil al día siguiente (puedes usar **Intentar de nuevo**: baraja las opciones y conserva tu mejor resultado).

- [ ] Hice los cuatro quizzes por dominio.
- [ ] Hice el simulacro con cronómetro.
- [ ] Identifiqué mi dominio más débil y lo repasé.
:::

:::step id="recursos" title="Recursos oficiales finales"
- [ ] [Currículo OTCA (CNCF)](https://github.com/cncf/curriculum/tree/main/otca) y [PDF del currículo](https://github.com/cncf/curriculum/blob/main/OTCA_Curriculum.pdf)
- [ ] [Página de la certificación en CNCF](https://www.cncf.io/training/certification/otca/)
- [ ] [Candidate Handbook](https://docs.linuxfoundation.org/tc-docs/certification/lf-handbook2) e [instrucciones importantes](https://docs.linuxfoundation.org/tc-docs/certification/important-instructions-mc)
- [ ] (Opcional) Curso gratuito [LFS148: Getting Started with OpenTelemetry](https://training.linuxfoundation.org/training/getting-started-with-opentelemetry-lfs148/)
- [ ] [Glosario oficial de OpenTelemetry](https://opentelemetry.io/docs/concepts/glossary/) · [español](https://opentelemetry.io/es/docs/concepts/glossary/)
:::
