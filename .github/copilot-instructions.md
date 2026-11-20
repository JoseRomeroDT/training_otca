# Instrucciones para asistentes de IA (GitHub Copilot, Claude…)

Este repositorio es un curso para la certificación OTCA publicado en GitHub Pages con el motor DocPages, más el código de sus laboratorios en GitHub Codespaces. Antes de crear o editar documentos, lee el skill [`.github/skills/documentation-pages/SKILL.md`](skills/documentation-pages/SKILL.md).

## Contenido del curso

- Español, con los términos técnicos en inglés (el examen es en inglés).
- **Nada inventado**: cada afirmación técnica enlaza a su fuente oficial (opentelemetry.io, la especificación de OpenTelemetry, los READMEs oficiales del Collector, CNCF o Linux Foundation). Si no hay fuente, no se escribe.
- Pesos de dominios y datos del examen: solo los de las páginas oficiales del examen.
- Si un documento cambia de forma significativa, sube su `version`.

## Formato de documentos (resumen del skill)

- El final del nombre decide el tipo: `documents/steps/**/{titulo}.procedure.steps.md` (material de estudio), `documents/steps/**/{titulo}.labguide.steps.md` (laboratorio) y `documents/tests/**/{titulo}.test.md` (quiz o simulacro).
- `slug` en kebab-case, único y estable; `updated` con formato `AAAA-MM-DD`; nada de HTML crudo.
- Tokens en lugar de URLs fijas del repositorio: `{{repo_url}}`, `{{owner}}`, `{{repo_name}}`, `{{branch}}`.
- En las preguntas, marca las correctas con `- [x]` o `answer="…"`; si no sabes cuál es la correcta según la documentación oficial, pregunta.
- Valida con `node scripts/validate-documents.mjs` y `node scripts/check-links.mjs` (solo Node 22+).

## Laboratorios

- Versiones fijadas (Python en `labs/requirements.txt`, imágenes en `labs/lab-env/compose.yaml`, Kubernetes en `labs/lab10-kubernetes/cluster-up.sh`).
- Configuraciones del Collector con los nombres de componentes vigentes en la versión fijada (`otlp_grpc`, `otlp_http`, `span_metrics`…) y validadas con `otelcol-contrib validate`.
- Todo cambio en `labs/` debe pasar `bash .github/scripts/e2e-labs.sh` (lo ejecuta el CI).

## Motor del sitio

`assets/`, `schemas/`, `scripts/`, `index.html` y `404.html` vienen de [DocPages](https://github.com/Edunzz/docpages); aquí solo se personalizaron `assets/js/config.js` (título) y los textos de categorías de `assets/js/i18n.js`. Los cambios al motor conviene hacerlos en DocPages y traerlos después. Todo archivo de código nuevo del motor empieza con el comentario de atribución:

```js
// Desarrollado por Jose Eduardo Romero Jimenez
// https://github.com/Edunzz
```
