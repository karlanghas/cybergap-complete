# 🛡️ CyberGAP - Sistema de Auditoría de Cumplimiento de Ciberseguridad

Sistema completo para realizar análisis GAP de ciberseguridad con gestión multi-empresa, cuestionarios personalizados, detección de divergencias y reportes exportables.

## 📋 Características Principales

### Gestión Multi-Empresa y Organizacional
- ✅ Crear y administrar múltiples empresas (clientes)
- ✅ Jerarquía de áreas por empresa (Gerencia, SOC, RRHH, Legal, etc.)
- ✅ Usuarios asociados a áreas específicas
- ✅ Configuración SMTP personalizada por empresa

### Gestión de Cuestionarios
- ✅ Banco de preguntas con categorías y puntajes
- ✅ Tipos de pregunta: selección única, múltiple, texto, escala, sí/no
- ✅ Asignación específica de preguntas a usuarios
- ✅ Links únicos (tokens) de un solo uso
- ✅ Expiración automática tras completar

### Detección de Divergencias
- ✅ Comparación automática de respuestas entre usuarios de la misma empresa
- ✅ Alertas de alineación cuando hay contradicciones
- ✅ Niveles de severidad: LOW, MEDIUM, HIGH, CRITICAL
- ✅ Panel de resolución de divergencias

### Reportes y Exportación
- ✅ Dashboard visual con métricas de cumplimiento
- ✅ Gráficos de cumplimiento por área y categoría
- ✅ Exportación a Excel (.xlsx)
- ✅ Vista detallada de respuestas

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────────┐
│                         NGINX (Reverse Proxy)                    │
│                              :80/:443                            │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐       ┌──────────────────────────┐   │
│  │     Frontend         │       │       Backend API        │   │
│  │     Vue.js 3         │       │       FastAPI            │   │
│  │     Tailwind CSS     │       │       SQLite/PostgreSQL  │   │
│  │        :80           │       │          :8000           │   │
│  └──────────────────────┘       └──────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

## 🛠️ Stack Tecnológico

| Componente | Tecnología |
|------------|------------|
| Backend | FastAPI (Python 3.11) |
| Frontend | Vue.js 3 + Tailwind CSS |
| Base de datos | SQLite (desarrollo) / PostgreSQL (producción) |
| Reverse Proxy | Nginx |
| Contenedores | Docker + Docker Compose |
| Compatibilidad | ARM64 (Raspberry Pi 5) / AMD64 |

## 📦 Estructura del Proyecto

```
cybergap/
├── backend/
│   ├── app/
│   │   ├── models.py           # Modelos SQLAlchemy
│   │   ├── schemas.py          # Schemas Pydantic
│   │   ├── database.py         # Configuración DB
│   │   ├── main.py             # App FastAPI
│   │   ├── routers/
│   │   │   ├── auth.py         # Autenticación
│   │   │   ├── companies.py    # Empresas
│   │   │   ├── areas.py        # Áreas
│   │   │   ├── users.py        # Usuarios
│   │   │   ├── questions.py    # Preguntas
│   │   │   ├── questionnaires.py  # Cuestionarios
│   │   │   └── public.py       # API pública (encuestas)
│   │   ├── services/
│   │   │   ├── divergence.py   # Detección de divergencias
│   │   │   └── reports.py      # Generación de reportes
│   │   └── utils/
│   │       ├── security.py     # JWT, bcrypt, encriptación
│   │       └── email.py        # Servicio de correo
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── Login.vue
│   │   │   ├── Companies.vue
│   │   │   ├── Areas.vue
│   │   │   ├── Users.vue
│   │   │   ├── Questions.vue
│   │   │   ├── Questionnaires.vue
│   │   │   ├── Reports.vue
│   │   │   └── Survey.vue
│   │   ├── components/
│   │   ├── stores/
│   │   └── router/
│   ├── package.json
│   └── Dockerfile
├── nginx/
│   ├── nginx.conf
│   └── conf.d/
│       └── default.conf
├── docker-compose.yml
├── .env.example
└── README.md
```

## 🚀 Instalación

### Prerequisitos
- Docker 20.10+
- Docker Compose 2.0+
- (Opcional) Portainer para gestión

### 1. Clonar el repositorio
```bash
git clone https://github.com/tu-usuario/cybergap.git
cd cybergap
```

### 2. Configurar variables de entorno
```bash
cp .env.example .env
nano .env
```

Variables importantes:
```env
# Seguridad (CAMBIAR EN PRODUCCIÓN)
SECRET_KEY=tu-clave-secreta-muy-larga-y-segura-de-32-chars
ENCRYPTION_KEY=tu-clave-encriptacion-32-bytes!!
DEFAULT_ADMIN_PASSWORD=admin123

# URL base para los links de encuestas
BASE_URL=https://tu-dominio.com

# Puerto expuesto
PORT=80
SSL_PORT=443
```

### 3. Construir y ejecutar
```bash
docker-compose up -d --build
```

### 4. Verificar el despliegue
```bash
# Estado de los contenedores
docker-compose ps

# Logs
docker-compose logs -f

# Health check
curl http://localhost/api/health
```

### 5. Acceder a la aplicación
- **Frontend**: http://localhost
- **API Docs**: http://localhost/api/docs
- **Credenciales iniciales**: `admin` / `admin123`

## 📱 Compatibilidad Raspberry Pi 5

El proyecto está optimizado para ARM64:

```bash
# En Raspberry Pi 5
docker-compose up -d --build

# Verificar arquitectura
docker inspect cybergap-api | grep Architecture
```

### Gestión con Portainer
1. Acceder a Portainer
2. Ir a "Stacks"
3. Crear nuevo stack desde git o subir docker-compose.yml
4. Configurar variables de entorno
5. Deploy

## 🔧 Configuración Avanzada

### Usar PostgreSQL
```yaml
# En docker-compose.yml, agregar servicio:
  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_DB: cybergap
      POSTGRES_USER: cybergap
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data

# Cambiar variable de entorno del backend:
  environment:
    - DATABASE_URL=postgresql://cybergap:${DB_PASSWORD}@postgres:5432/cybergap
```

### Habilitar HTTPS
1. Obtener certificados SSL (Let's Encrypt o propios)
2. Montar en volumen `cybergap_ssl`:
```bash
docker cp fullchain.pem cybergap-nginx:/etc/nginx/ssl/cert.pem
docker cp privkey.pem cybergap-nginx:/etc/nginx/ssl/key.pem
```
3. Descomentar bloque HTTPS en `nginx/conf.d/default.conf`
4. Reiniciar nginx: `docker-compose restart nginx`

### Configurar SMTP por Empresa
1. Ir a Empresas → Seleccionar empresa
2. Configuración SMTP:
   - Servidor: smtp.gmail.com
   - Puerto: 587
   - Usuario: correo@empresa.com
   - Contraseña: app-password
3. Probar conexión

## 📊 Uso del Sistema

### Flujo de Trabajo Típico

1. **Crear Empresa** → Dashboard → Empresas → Nueva empresa
2. **Definir Áreas** → Seleccionar empresa → Agregar áreas jerárquicas
3. **Agregar Usuarios** → Usuarios → Crear usuarios por área
4. **Cargar Preguntas** → Banco de Preguntas → Importar o crear
5. **Crear Cuestionario** → Cuestionarios → Nuevo cuestionario
6. **Asignar** → Seleccionar usuarios y preguntas específicas
7. **Enviar Tokens** → Los usuarios reciben links por correo
8. **Monitorear** → Ver progreso y divergencias en tiempo real
9. **Generar Reporte** → Exportar resultados a Excel

### Detección de Divergencias

El sistema detecta automáticamente cuando:
- Dos usuarios de la misma empresa responden diferente a la misma pregunta
- Asigna nivel de severidad basado en la diferencia de puntaje
- Permite resolver divergencias con notas explicativas

## 🔒 Seguridad

- Autenticación JWT con tokens de acceso
- Contraseñas hasheadas con bcrypt
- Encriptación de contraseñas SMTP con Fernet
- Rate limiting en endpoints de login
- Headers de seguridad HTTP
- Tokens de encuesta de un solo uso

## 🧪 Desarrollo

### Ejecutar en modo desarrollo

Backend:
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

Frontend:
```bash
cd frontend
npm install
npm run dev
```

### Tests
```bash
cd backend
pytest
```

## 📝 API Reference

Documentación interactiva disponible en `/api/docs` (Swagger UI) y `/api/redoc` (ReDoc).

### Endpoints Principales

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | /api/auth/login | Autenticación |
| GET | /api/companies | Listar empresas |
| POST | /api/questionnaires | Crear cuestionario |
| POST | /api/questionnaires/{id}/send-tokens | Enviar emails |
| GET | /api/public/survey/{token} | Obtener encuesta (público) |
| POST | /api/public/survey/{token}/respond | Enviar respuesta |
| GET | /api/reports/company/{id}/export | Exportar Excel |

## 🤝 Contribuir

1. Fork del repositorio
2. Crear branch de feature (`git checkout -b feature/nueva-funcionalidad`)
3. Commit de cambios (`git commit -m 'Agregar nueva funcionalidad'`)
4. Push al branch (`git push origin feature/nueva-funcionalidad`)
5. Crear Pull Request

## 📄 Licencia

MIT License - Ver archivo `LICENSE` para más detalles.

## 🙋 Soporte

Para reportar bugs o solicitar features, crear un issue en el repositorio.

---

**CyberGAP** - Desarrollado para simplificar las auditorías de cumplimiento de ciberseguridad 🛡️
