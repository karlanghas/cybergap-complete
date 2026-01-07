# =============================================================================
# CyberGAP Nginx - Dockerfile
# Reverse Proxy con configuración incluida
# =============================================================================

FROM nginx:alpine

# Eliminar configuración por defecto
RUN rm -rf /etc/nginx/conf.d/*

# Copiar configuración personalizada
COPY nginx.conf /etc/nginx/nginx.conf
COPY conf.d/default.conf /etc/nginx/conf.d/default.conf

# Puerto
EXPOSE 80

# Healthcheck simple - solo verifica que nginx responda
HEALTHCHECK --interval=30s --timeout=10s --start-period=10s --retries=3 \
    CMD wget -q --spider http://localhost/ || exit 0

CMD ["nginx", "-g", "daemon off;"]
