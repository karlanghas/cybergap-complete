# =============================================================================
# CyberGAP Frontend - Dockerfile
# Compatible con ARM64 (Raspberry Pi 5) y AMD64
# REBUILD: 2025-01-08-v13
# =============================================================================

# Build stage
FROM node:20-alpine AS builder

# Aumentar memoria para Node en sistemas con poca RAM
ENV NODE_OPTIONS="--max-old-space-size=1024"

WORKDIR /app

# Cache bust para forzar rebuild
RUN echo "Build timestamp: $(date)"

# Copiar package.json
COPY package.json ./

# Instalar dependencias con más verbosidad
RUN echo "📦 Instalando dependencias..." && \
    npm install 2>&1 && \
    echo "✅ Dependencias instaladas"

# Copiar el resto de archivos
COPY . .

# Build argument for API URL
ARG VITE_API_URL=/api
ENV VITE_API_URL=$VITE_API_URL

# Build con información de debug
RUN echo "🔨 Construyendo aplicación..." && \
    npm run build 2>&1 && \
    echo "✅ Build completado" && \
    ls -la dist/

# Production stage
FROM nginx:alpine

# Copiar archivos construidos
COPY --from=builder /app/dist /usr/share/nginx/html

# Configuración nginx para SPA
RUN cat > /etc/nginx/conf.d/default.conf << 'EOF'
server {
    listen 80;
    server_name _;
    root /usr/share/nginx/html;
    index index.html;
    
    # Gzip
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;
    
    # SPA fallback
    location / {
        try_files $uri $uri/ /index.html;
    }
    
    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
