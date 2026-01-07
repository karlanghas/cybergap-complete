# =============================================================================
# CyberGAP Backend - Dockerfile
# Optimizado para ARM64 (Raspberry Pi 5) y AMD64
# =============================================================================

FROM python:3.11-slim-bookworm

# Metadatos
LABEL maintainer="CyberGAP"
LABEL description="CyberGAP - Sistema de Auditoría de Cumplimiento"
LABEL version="1.0.0"

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    libpq-dev \
    libffi-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY ./app ./app
COPY ./start.sh ./start.sh
RUN chmod +x ./start.sh

# Crear directorio de datos y logs con permisos correctos
RUN mkdir -p /app/data /app/logs && chmod 777 /app/data /app/logs

# Puerto
EXPOSE 8085

# Comando por defecto con script de inicio
CMD ["./start.sh"]
