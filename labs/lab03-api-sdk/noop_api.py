"""Lab 3 · Paso 1: la API sin SDK no hace nada (implementación mínima "no-op").

La especificación exige que, si la aplicación solo depende de la API y nadie
registra un SDK, las llamadas sigan funcionando sin fallar y sin producir
telemetría.
Fuente: https://opentelemetry.io/docs/specs/otel/library-guidelines/#api-and-minimal-implementation

Ejecutar: python noop_api.py
"""
from opentelemetry import trace

tracer = trace.get_tracer("lab03.noop")

with tracer.start_as_current_span("operacion-sin-sdk") as span:
    span.set_attribute("lab.nota", "este atributo no va a ningún lado")
    print("Tipo de span         :", type(span).__name__)
    print("¿Está grabando?      :", span.is_recording())
    print("¿SpanContext válido? :", span.get_span_context().is_valid)

print("\nSin SDK no se exporta nada, pero el código no falló: la API devolvió")
print("objetos válidos que no hacen nada. Así una librería puede instrumentarse")
print("con la API sin obligar a sus usuarios a usar OpenTelemetry.")
