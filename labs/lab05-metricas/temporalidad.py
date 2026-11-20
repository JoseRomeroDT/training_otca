"""Lab 5 · Temporalidad de agregación: CUMULATIVE frente a DELTA.

Suma 5 a un Counter tres veces y exporta a la consola cada ~2 s.
  - cumulative (por defecto del SDK): cada exportación informa el total desde el inicio → 5, 10, 15
  - delta: cada exportación informa solo lo ocurrido desde la exportación anterior → 5, 5, 5

Fuentes:
  https://opentelemetry.io/docs/specs/otel/metrics/data-model/#temporality
  https://opentelemetry.io/docs/languages/python/exporters/  (OTEL_EXPORTER_OTLP_METRICS_TEMPORALITY_PREFERENCE)

Ejecutar: python temporalidad.py cumulative
          python temporalidad.py delta
"""
import sys
import time

from opentelemetry.sdk.metrics import Counter, MeterProvider
from opentelemetry.sdk.metrics.export import (
    AggregationTemporality,
    ConsoleMetricExporter,
    PeriodicExportingMetricReader,
)

modo = (sys.argv[1] if len(sys.argv) > 1 else "cumulative").lower()
if modo not in ("cumulative", "delta"):
    sys.exit("Uso: python temporalidad.py [cumulative|delta]")

preferencia = {Counter: AggregationTemporality.DELTA} if modo == "delta" else {}


def formato_compacto(metrics_data):
    """Una línea por punto de datos, en lugar del JSON completo."""
    lineas = []
    for rm in metrics_data.resource_metrics:
        for sm in rm.scope_metrics:
            for metric in sm.metrics:
                temporalidad = metric.data.aggregation_temporality.name
                for punto in metric.data.data_points:
                    lineas.append(f"  {metric.name}  temporalidad={temporalidad:<10}  valor={punto.value}")
    return "\n".join(lineas) + "\n" if lineas else ""


exporter = ConsoleMetricExporter(preferred_temporality=preferencia, formatter=formato_compacto)
reader = PeriodicExportingMetricReader(exporter, export_interval_millis=2_000)
provider = MeterProvider(metric_readers=[reader])
contador = provider.get_meter("lab05.temporalidad").create_counter("demo.eventos")

print(f"Modo: {modo}")
for i in range(3):
    contador.add(5)
    print(f"add(5) n.º {i + 1}")
    time.sleep(2.5)
provider.shutdown()
