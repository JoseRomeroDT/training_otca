# Laboratorios

Código y entorno de los laboratorios del entrenamiento OTCA. Las guías paso a paso están en el sitio del curso (`documents/steps/labs/`).

## Entorno (`lab-env/`)

| Script | Qué hace |
|---|---|
| `up.sh` | Levanta Collector + Jaeger + Prometheus y comprueba que respondan |
| `status.sh` | Comprueba el entorno e imprime las URLs (en Codespaces, las del reenvío de puertos) |
| `use-collector-config.sh <archivo> [collector\|gateway]` | Valida una configuración con `otelcol-contrib validate` y la activa |
| `reset-collector.sh` | Vuelve a la configuración del curso y detiene el gateway del Lab 9 |
| `down.sh` | Detiene todo (la configuración activa en `active/` se conserva) |
| `smoke_test.py` | Envía un span, una métrica y un log de prueba (Lab 0) |

Puertos: OTLP gRPC `4317` · OTLP HTTP `4318` · Jaeger `16686` · Prometheus `9090` · métricas internas del Collector `8888` · zPages `55679` · health_check `13133` · pprof `1777`.

## Laboratorios

| Carpeta | Laboratorio | Qué contiene |
|---|---|---|
| `lab02-zero-code/` | 2 · Zero-code | App Flask del Getting Started oficial, sin código de OpenTelemetry |
| `lab03-api-sdk/` | 3 · API y SDK | `noop_api.py` (API sin SDK) y `app.py` (SDK configurado a mano, processor propio) |
| `lab04-trazas/` | 4 · Trazas | `dice_server.py` y `player.py`: trazado distribuido, errores y sampling ParentBased |
| `lab05-metricas/` | 5 · Métricas | `dice_server.py` con 5 instrumentos y una View; `temporalidad.py` |
| `lab06-logs-contexto/` | 6 · Logs y contexto | `frontend.py` y `backend.py` con propagación manual, baggage y logs correlacionados |
| `lab07-configuracion/` | 7 · Configuración | `app.py` sin OpenTelemetry y `otel.env` con toda la configuración `OTEL_*` |
| `lab08-collector/` | 8 · Collector | `inicio.yaml` (mínimo) y `solucion.yaml` |
| `lab09-ottl-gateway/` | 9 · OTTL y gateway | `agent.yaml` y `gateway.yaml` (transform, filter, span_metrics) |
| `lab10-kubernetes/` | 10 · Kubernetes | Scripts de kind, recursos del Operator y la app (`app/`) |
| `lab11-depuracion/` | 11 · Depuración | Configuraciones rotas a propósito y sus soluciones |

El Lab 1 usa la [OpenTelemetry Demo](https://github.com/open-telemetry/opentelemetry-demo) oficial (versión 3.1.0), que se clona fuera de este repositorio.

## Versiones

Todas las versiones están fijadas: `requirements.txt` (Python), `lab-env/compose.yaml` (imágenes), `lab10-kubernetes/cluster-up.sh` (cert-manager y Operator) y `.devcontainer/post-create.sh` (kind). Al actualizar una, ejecuta `bash .github/scripts/e2e-labs.sh` (y `e2e-lab10.sh` para Kubernetes) o deja que lo haga el CI.
