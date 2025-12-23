# =============================================================================
# CyberGAP Backend - Dockerfile
# Optimizado para ARM64 (Raspberry Pi 5)
# =============================================================================

FROM python:3.11-slim-bookworm

# Argumentos de build
ARG TARGETPLATFORM
ARG BUILDPLATFORM

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
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primero (para cache de Docker)
COPY requirements.txt .

# Instalar dependencias Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY ./app ./app

# Crear directorio de datos
RUN mkdir -p /app/data

# Crear usuario no-root
RUN useradd -m -u 1000 cybergap && \
    chown -R cybergap:cybergap /app
USER cybergap

# Puerto
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8180/api/health')" || exit 1

# Comando por defecto
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8180"]
