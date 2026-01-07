# 🐳 Despliegue CyberGAP con Portainer + GitHub

## 📋 Requisitos

- Repositorio en GitHub con el código de CyberGAP
- Raspberry Pi con Portainer instalado
- Acceso a Portainer (http://IP:9000)

---

## 🚀 Paso a Paso

### 1️⃣ Subir código a GitHub

```bash
# En tu máquina local
cd cybergap
git init
git add .
git commit -m "CyberGAP v1.0"
git branch -M main
git remote add origin https://github.com/TU_USUARIO/cybergap.git
git push -u origin main
```

---

### 2️⃣ Crear Stack en Portainer

1. Acceder a **Portainer** → http://IP_RASPBERRY:9000

2. Menú lateral → **Stacks**

3. Click en **+ Add stack**

4. Configurar:

```
┌─────────────────────────────────────────────────────────────────┐
│  Name: cybergap                                                 │
├─────────────────────────────────────────────────────────────────┤
│  Build method:  ○ Web editor                                    │
│                 ○ Upload                                        │
│                 ● Repository    ← SELECCIONAR ESTE              │
└─────────────────────────────────────────────────────────────────┘
```

---

### 3️⃣ Configurar Repositorio

```
┌─────────────────────────────────────────────────────────────────┐
│  Repository URL                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ https://github.com/TU_USUARIO/cybergap                    │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Repository reference (branch/tag)                              │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ main                                                      │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  Compose path                                                   │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ docker-compose.yml                                        │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

**Si el repositorio es privado:**
- Marcar ☑️ **Authentication**
- Ingresar usuario de GitHub
- Ingresar **Personal Access Token** (no la contraseña)
  - Crear en: GitHub → Settings → Developer settings → Personal access tokens

---

### 4️⃣ Variables de Entorno (Environment Variables)

Scroll hacia abajo hasta la sección **Environment variables**.

Click en **+ Add an environment variable** para cada una:

| Name | Value |
|------|-------|
| `SECRET_KEY` | `K7xP9mN2vQ4wR8tY6uI3oL5jH1gF0dS2aE4cB7nM9` |
| `ENCRYPTION_KEY` | `X9kL2mN4pQ7rS1tU6vW8xY0zA3bC5dE7` |
| `DEFAULT_ADMIN_PASSWORD` | `MiPasswordSeguro123!` |
| `BASE_URL` | `http://192.168.1.100` |
| `TZ` | `America/Santiago` |
| `PORT` | `80` |

```
┌─────────────────────────────────────────────────────────────────┐
│  Environment variables                                          │
│                                                                 │
│  ┌─────────────────────┬───────────────────────────────────┐   │
│  │ name                │ value                             │   │
│  ├─────────────────────┼───────────────────────────────────┤   │
│  │ SECRET_KEY          │ K7xP9mN2vQ4wR8tY6uI3oL5jH1gF...  │ ✕ │
│  ├─────────────────────┼───────────────────────────────────┤   │
│  │ ENCRYPTION_KEY      │ X9kL2mN4pQ7rS1tU6vW8xY0zA3bC...  │ ✕ │
│  ├─────────────────────┼───────────────────────────────────┤   │
│  │ DEFAULT_ADMIN_PASS..│ MiPasswordSeguro123!              │ ✕ │
│  ├─────────────────────┼───────────────────────────────────┤   │
│  │ BASE_URL            │ http://192.168.1.100              │ ✕ │
│  ├─────────────────────┼───────────────────────────────────┤   │
│  │ TZ                  │ America/Santiago                  │ ✕ │
│  ├─────────────────────┼───────────────────────────────────┤   │
│  │ PORT                │ 80                                │ ✕ │
│  └─────────────────────┴───────────────────────────────────┘   │
│                                                                 │
│  [+ Add an environment variable]                                │
└─────────────────────────────────────────────────────────────────┘
```

---

### 5️⃣ Opciones Adicionales (Opcional)

```
┌─────────────────────────────────────────────────────────────────┐
│  ☑️ Enable automatic updates                                    │
│     GitOps updates: Re-pull and redeploy when repo changes      │
│                                                                 │
│  Polling interval: [ 5m ▼ ]                                     │
└─────────────────────────────────────────────────────────────────┘
```

Si activas esto, Portainer revisará el repositorio cada 5 minutos y actualizará automáticamente cuando hagas push.

---

### 6️⃣ Desplegar

1. Click en **Deploy the stack**

2. Esperar 3-5 minutos (primera vez tarda más por el build)

3. Ver progreso en **Containers**

```
┌─────────────────────────────────────────────────────────────────┐
│  Stack deployed successfully!                                   │
│                                                                 │
│  Containers:                                                    │
│  ✅ cybergap-api       running    healthy                       │
│  ✅ cybergap-frontend  running                                  │
│  ✅ cybergap-nginx     running    healthy                       │
└─────────────────────────────────────────────────────────────────┘
```

---

## ✅ Verificar Despliegue

| Recurso | URL |
|---------|-----|
| **Frontend** | http://192.168.1.100 |
| **API Docs** | http://192.168.1.100/api/docs |
| **Health Check** | http://192.168.1.100/api/health |

**Credenciales iniciales:**
- Usuario: `admin`
- Password: `[tu DEFAULT_ADMIN_PASSWORD]`

---

## 🔑 Generar Claves Seguras

Ejecutar en terminal:

```bash
# SECRET_KEY (mínimo 32 caracteres)
openssl rand -base64 32
# Ejemplo: K7xP9mN2vQ4wR8tY6uI3oL5jH1gF0dS2aE4cB7nM9xZq

# ENCRYPTION_KEY (exactamente 32 caracteres)
openssl rand -base64 24 | head -c 32
# Ejemplo: X9kL2mN4pQ7rS1tU6vW8xY0zA3bC5dE7
```

---

## 🔄 Actualizar desde GitHub

### Opción A: Automático (si activaste GitOps)
Solo haz `git push` y Portainer actualizará automáticamente.

### Opción B: Manual
1. **Stacks** → **cybergap**
2. Click en **Pull and redeploy**
3. Marcar ☑️ **Re-pull image and redeploy**
4. Click **Update**

---

## 🔧 Solución de Problemas

### Error: "Build failed"
- Verificar que el repositorio tenga los archivos `Dockerfile` en:
  - `backend/Dockerfile`
  - `frontend/Dockerfile`

### Error: "Cannot connect to repository"
- Verificar URL del repositorio
- Si es privado, verificar token de acceso

### Ver logs
**Containers** → **cybergap-api** → **Logs**

### Reiniciar
**Stacks** → **cybergap** → **Stop** → **Start**

---

## 📁 Estructura Esperada del Repositorio

```
cybergap/
├── docker-compose.yml      ← Portainer lee este archivo
├── backend/
│   ├── Dockerfile
│   ├── requirements.txt
│   └── app/
│       ├── main.py
│       ├── models.py
│       └── ...
├── frontend/
│   ├── Dockerfile
│   ├── package.json
│   └── src/
│       └── ...
└── nginx/
    ├── nginx.conf
    └── conf.d/
        └── default.conf
```

---

## 📝 Variables de Entorno - Referencia

| Variable | Descripción | Obligatorio | Ejemplo |
|----------|-------------|-------------|---------|
| `SECRET_KEY` | Clave JWT (32+ chars) | ✅ | `openssl rand -base64 32` |
| `ENCRYPTION_KEY` | Clave AES (32 chars exactos) | ✅ | `openssl rand -base64 24 \| head -c 32` |
| `DEFAULT_ADMIN_PASSWORD` | Password admin inicial | ✅ | `MiPassword123!` |
| `BASE_URL` | URL pública | ✅ | `http://192.168.1.100` |
| `TZ` | Zona horaria | ⚪ | `America/Santiago` |
| `PORT` | Puerto HTTP | ⚪ | `80` |
| `DEBUG` | Modo debug | ⚪ | `false` |

---

¡Listo! Tu CyberGAP está desplegado y conectado a GitHub 🚀
