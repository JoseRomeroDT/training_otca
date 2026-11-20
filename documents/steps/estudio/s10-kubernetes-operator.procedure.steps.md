---
title: "Sesión 10 · Operator, Kubernetes y escalamiento"
description: "El OpenTelemetry Operator (Collector y auto-instrumentación como recursos de Kubernetes), sus modos de despliegue, cómo y cuándo escalar el Collector, y buenas prácticas de producción. Dominio 3 (26 %)."
slug: "s10-kubernetes-operator"
type: "steps"
version: "1.0.0"
updated: "2026-11-20"
tags: [dominio-3, kubernetes, operator, escalamiento]
duration: "2 horas"
level: "advanced"
objectives:
  - "Instalar el OpenTelemetry Operator y crear un Collector gestionado."
  - "Auto-instrumentar cargas en Kubernetes con el recurso Instrumentation y anotaciones."
  - "Decidir cuándo y cómo escalar el Collector (stateless, scrapers y stateful)."
  - "Aplicar buenas prácticas de producción."
links:
  - label: "Laboratorio 10: Kubernetes"
    url: "../labs/lab10-kubernetes.labguide.steps.md"
    icon: "flask-conical"
    highlight: true
  - label: "Quiz del Dominio 3"
    url: "../../tests/quiz-d3-collector.test.md"
    icon: "graduation-cap"
  - label: "Ruta del curso"
    url: "00-ruta-otca.procedure.steps.md"
    icon: "list-checks"
---

# {{ title }}

**Dominio 3 · The OpenTelemetry Collector (26 %)** — competencias *Deployment* y *Scaling*. Cierra el dominio: al terminar, haz el quiz del Dominio 3.

:::step id="operator" title="El OpenTelemetry Operator"
De [Kubernetes Operator](https://opentelemetry.io/docs/platforms/kubernetes/operator/) ([español](https://opentelemetry.io/es/docs/platforms/kubernetes/operator/)):

- Es una implementación de un *Kubernetes Operator* que gestiona el **OpenTelemetry Collector** y la **auto-instrumentación** de las cargas con las librerías de instrumentación de OpenTelemetry.
- Instalación: requiere **cert-manager**; luego `kubectl apply -f …/opentelemetry-operator.yaml` (o con el [Helm chart](https://opentelemetry.io/docs/platforms/kubernetes/helm/operator/) u OperatorHub).
- Recurso **`OpenTelemetryCollector`** (`apiVersion: opentelemetry.io/v1beta1`): la configuración del Collector va en `spec.config`. Con `mode: deployment` el Operator crea un Service llamado `<nombre>-collector`.
- **Modos** (`spec.mode`): `deployment` (por defecto), `daemonset`, `statefulset` y `sidecar` ([deployment modes](https://github.com/open-telemetry/opentelemetry-operator/blob/main/docs/collector/deployment-modes.md)).
- Por defecto usa la imagen del Collector **core**; con Helm, la `otelcol-k8s`. Si necesitas otro componente, construye tu distribución con **ocb**.

- [ ] Sé qué gestiona el Operator y qué modos de despliegue ofrece.
:::

:::step id="autoinstr" title="Auto-instrumentación con el recurso Instrumentation"
De [Injecting auto-instrumentation](https://opentelemetry.io/docs/platforms/kubernetes/operator/automatic/):

- El recurso **`Instrumentation`** define endpoint del exporter, propagadores, sampler y opciones por lenguaje. **Debe existir antes** de desplegar la app; si no, el *init container* no se crea.
- Se activa con una **anotación** en el template del pod: `instrumentation.opentelemetry.io/inject-python: "true"` (también `inject-java`, `inject-nodejs`, `inject-dotnet`, `inject-go`, e `inject-sdk` para inyectar solo variables). Valores: `"true"`, `"nombre"`, `"otro-namespace/nombre"` o `"false"`.
- El Operator agrega el init container **`opentelemetry-auto-instrumentation`**, que deja el agente disponible para el contenedor de la app.
- **Python** usa OTLP sobre **`http/protobuf`** (gRPC no está soportado), por eso el endpoint apunta al puerto **4318** del Collector. Desde el Operator v0.108.0, `OTEL_EXPORTER_OTLP_PROTOCOL` se fija solo en `http/protobuf` para Python.
- La imagen de Python del Operator se construye para **una versión de Python** (glibc): los paquetes con código binario dependen de ella ([Python · Operator](https://opentelemetry.io/docs/zero-code/python/operator/)).
- **Recursos**: el Operator calcula atributos como `k8s.pod.name` y `service.name` (por orden: anotación `resource.opentelemetry.io/service.name`, etiqueta `app.kubernetes.io/name` si se habilita, nombre del Deployment, ReplicaSet, …). Prioridad: variables `OTEL_*` > anotaciones > etiquetas > metadatos del pod > `spec.resource` del Instrumentation.

- [ ] Sé qué pasos y en qué orden se necesitan para auto-instrumentar un pod.
:::

:::step id="cuando-escalar" title="Cuándo escalar el Collector"
De [Scaling the Collector](https://opentelemetry.io/docs/collector/scaling/), con sus métricas internas:

- `otelcol_processor_refused_spans` (y equivalentes por señal): el `memory_limiter` está rechazando datos con frecuencia → considera **escalar**.
- `otelcol_exporter_queue_size` frente a `otelcol_exporter_queue_capacity`: la guía es **escalar al 60-70 % de la capacidad**, reducir si se mantiene bajo y conservar un mínimo de réplicas (por ejemplo, tres) por resiliencia. Si la cola se llena, se rechazan datos (`otelcol_exporter_enqueue_failed_spans`).
- Receivers que hacen *scraping* (p. ej. `prometheus`): escalar o repartir cuando el scrape de todos los targets se acerca al intervalo de scrape.

**Cuándo NO escalar**: si el backend no da abasto o la red hacia él está saturada, más Collectors no ayudan (incluso empeoran). Señales: cola siempre cerca de su capacidad aun después de agrandarla, o aumento de `otelcol_exporter_send_failed_spans` (fallos permanentes de envío).

- [ ] Sé qué métricas internas mirar antes de escalar.
:::

:::step id="como-escalar" title="Cómo escalar según el tipo de componente"
De [Scaling · How to scale](https://opentelemetry.io/docs/collector/scaling/#how-to-scale):

| Tipo | Ejemplos | Cómo se escala |
|---|---|---|
| **Stateless** (la mayoría) | `otlp` receiver, `batch`, `attributes` | Más réplicas detrás de un **balanceador**. Con gRPC usa uno de capa 7: uno de capa 4 puede fijar la conexión a una sola instancia |
| **Scrapers** | `prometheus`, `host_metrics` | **Repartir** (*shard*) los targets entre instancias; en Kubernetes, con el **Target Allocator** del Operator |
| **Stateful** | `tail_sampling`, métricas derivadas de spans | Una capa previa con el exporter **`loadbalancing`** para que los datos de una misma traza o servicio lleguen a la misma instancia |

- El Operator integra **HPA**: `spec.autoscaler` (`minReplicas`, `maxReplicas`, `targetCPUUtilization`, `targetMemoryUtilization`) con `spec.resources` definidos; solo en modo `deployment` o `statefulset` y requiere **Metrics Server** ([HPA](https://opentelemetry.io/docs/platforms/kubernetes/operator/horizontal-pod-autoscaling/)).
- El **Target Allocator** reparte los targets de Prometheus entre un grupo de Collectors y descubre los recursos personalizados de Prometheus ([Target Allocator](https://opentelemetry.io/docs/platforms/kubernetes/operator/target-allocator/)).
- En Kubernetes es común un **DaemonSet** (agente por nodo) más un Collector central; con pocos nodos y muchos pods, los **sidecars** pueden balancear mejor las conexiones gRPC.

- [ ] Sé cómo escalar cada tipo de componente.
:::

:::step id="produccion" title="Buenas prácticas de producción"
- Envía a un **Collector** en lugar de directo al backend (secretos, reintentos y enriquecimiento centralizados) ([Operator](https://opentelemetry.io/docs/platforms/kubernetes/operator/automatic/#create-an-opentelemetry-collector-optional)).
- Usa `k8s_attributes` para agregar metadatos de Kubernetes y `resource_detection` para los del host; con varios Collectors, asegura un **único escritor** por flujo de métricas ([gateway](https://opentelemetry.io/docs/collector/deploy/gateway/#best-practices)).
- `memory_limiter` en todos los Collectors y monitoreo de sus métricas internas.
- Componentes del Collector clave en Kubernetes: Kubernetes Attributes Processor, Kubeletstats Receiver, Filelog Receiver, Kubernetes Cluster Receiver, Kubernetes Objects Receiver, Prometheus Receiver y Host Metrics Receiver ([Important components for Kubernetes](https://opentelemetry.io/docs/platforms/kubernetes/collector/components/)).
:::

:::step id="lecturas" title="Lecturas oficiales"
- [ ] [Kubernetes Operator](https://opentelemetry.io/docs/platforms/kubernetes/operator/) · [español](https://opentelemetry.io/es/docs/platforms/kubernetes/operator/)
- [ ] [Injecting auto-instrumentation](https://opentelemetry.io/docs/platforms/kubernetes/operator/automatic/)
- [ ] [Scaling the Collector](https://opentelemetry.io/docs/collector/scaling/)
- [ ] [Horizontal Pod Autoscaling](https://opentelemetry.io/docs/platforms/kubernetes/operator/horizontal-pod-autoscaling/) y [Target Allocator](https://opentelemetry.io/docs/platforms/kubernetes/operator/target-allocator/)
- [ ] Repositorio [opentelemetry-operator](https://github.com/open-telemetry/opentelemetry-operator)
:::

:::step id="repaso" title="Puntos clave para repasar"
- Operator = `OpenTelemetryCollector` + `Instrumentation`; requiere cert-manager.
- Modos: deployment (por defecto), daemonset, statefulset, sidecar.
- Instrumentation **antes** que la app; anotación `inject-<lenguaje>`; init container `opentelemetry-auto-instrumentation`.
- Python por el Operator → `http/protobuf` → puerto 4318.
- Escalar al 60-70 % de la cola; no escalar si el problema es el backend.
- Stateless → balanceador; scrapers → sharding/Target Allocator; stateful → `loadbalancing` exporter.

- [ ] Repasé los puntos clave.
- [ ] Hice el [Laboratorio 10](../labs/lab10-kubernetes.labguide.steps.md).
- [ ] Hice el [quiz del Dominio 3](../../tests/quiz-d3-collector.test.md).
:::
