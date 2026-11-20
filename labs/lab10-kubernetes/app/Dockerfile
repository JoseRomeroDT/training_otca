# Imagen de la app del Lab 10.
# Usa la MISMA versión menor de Python con la que el Operator v0.163.0 construye su
# imagen de auto-instrumentación (python:3.15, glibc): los paquetes con código
# binario dependen de la versión de Python. Ver:
# https://opentelemetry.io/docs/zero-code/python/operator/#libraries-with-binary-wheels
FROM python:3.15-slim

WORKDIR /app
RUN pip install --no-cache-dir flask==3.1.3
COPY app.py .

EXPOSE 8080
CMD ["python", "app.py"]
