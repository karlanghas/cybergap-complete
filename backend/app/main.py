"""
CyberGAP - Aplicación de Auditoría de Cumplimiento de Ciberseguridad
Main FastAPI Application
"""
import os
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from .database import engine, Base, init_db, get_db
from .models import AdminUser
from .utils.security import hash_password
from .routers import (
    auth_router,
    companies_router,
    areas_router,
    users_router,
    questions_router,
    category_router,
    questionnaires_router,
    public_router
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager para inicialización y cleanup"""
    # Startup
    print("🚀 Iniciando CyberGAP...")
    init_db()
    await create_default_admin()
    print("✅ CyberGAP listo!")
    yield
    # Shutdown
    print("👋 Cerrando CyberGAP...")


async def create_default_admin():
    """Crear usuario admin por defecto si no existe"""
    from sqlalchemy.orm import Session
    from .database import SessionLocal
    
    db = SessionLocal()
    try:
        admin = db.query(AdminUser).filter(AdminUser.username == "admin").first()
        if not admin:
            default_password = os.getenv("DEFAULT_ADMIN_PASSWORD", "admin123")
            admin = AdminUser(
                username="admin",
                email="admin@cybergap.local",
                full_name="Administrador",
                hashed_password=hash_password(default_password),
                is_superadmin=True,
                is_active=True
            )
            db.add(admin)
            db.commit()
            print(f"👤 Admin creado: admin / {default_password}")
    finally:
        db.close()


# Crear aplicación FastAPI
app = FastAPI(
    title="CyberGAP API",
    description="""
    ## Sistema de Auditoría de Cumplimiento de Ciberseguridad
    
    CyberGAP permite realizar análisis GAP de ciberseguridad mediante:
    
    - 🏢 **Gestión Multi-Empresa**: Administrar múltiples clientes/empresas
    - 📊 **Cuestionarios Personalizados**: Crear y asignar preguntas específicas
    - 🔗 **Enlaces Únicos**: Tokens de un solo uso para respuestas seguras
    - ⚠️ **Detección de Divergencias**: Identificar contradicciones en respuestas
    - 📈 **Reportes y Exportación**: Dashboards y exportación a Excel
    """,
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json"
)

# CORS Configuration
origins = [
    "http://localhost:3000",
    "http://localhost:5173",
    "http://localhost:8080",
    "http://127.0.0.1:3000",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:8080",
]

# Agregar origen personalizado desde variable de entorno
custom_origin = os.getenv("CORS_ORIGIN")
if custom_origin:
    origins.append(custom_origin)

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception Handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handler personalizado para errores de validación"""
    errors = []
    for error in exc.errors():
        field = ".".join(str(x) for x in error["loc"][1:]) if len(error["loc"]) > 1 else error["loc"][0]
        errors.append({
            "field": field,
            "message": error["msg"],
            "type": error["type"]
        })
    
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "Error de validación",
            "errors": errors
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handler general para excepciones no manejadas"""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "success": False,
            "message": "Error interno del servidor",
            "detail": str(exc) if os.getenv("DEBUG", "false").lower() == "true" else None
        }
    )


# Health Check
@app.get("/api/health", tags=["Sistema"])
async def health_check():
    """Verificar estado del sistema"""
    return {
        "status": "healthy",
        "service": "CyberGAP API",
        "version": "1.0.0"
    }


# Registrar Routers
app.include_router(auth_router, prefix="/api")
app.include_router(companies_router, prefix="/api")
app.include_router(areas_router, prefix="/api")
app.include_router(users_router, prefix="/api")
app.include_router(category_router, prefix="/api")
app.include_router(questions_router, prefix="/api")
app.include_router(questionnaires_router, prefix="/api")
app.include_router(public_router, prefix="/api")


# Router de Reportes
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from .services.reports import ReportService
from .routers.auth import get_current_admin

reports_router = APIRouter(prefix="/reports", tags=["Reportes"])


@reports_router.get("/dashboard")
async def get_dashboard(
    company_id: int = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener datos del dashboard"""
    service = ReportService(db)
    return service.get_dashboard_stats(company_id)


@reports_router.get("/company/{company_id}")
async def get_company_report(
    company_id: int,
    questionnaire_id: int = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener reporte completo de una empresa"""
    service = ReportService(db)
    return service.generate_company_report(company_id, questionnaire_id)


@reports_router.get("/company/{company_id}/export")
async def export_company_report(
    company_id: int,
    questionnaire_id: int = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Exportar reporte a Excel"""
    from fastapi.responses import FileResponse
    import tempfile
    
    service = ReportService(db)
    
    # Crear archivo temporal
    with tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx") as tmp:
        filepath = tmp.name
    
    service.export_to_excel(company_id, filepath, questionnaire_id)
    
    return FileResponse(
        path=filepath,
        filename=f"reporte_cybergap_{company_id}.xlsx",
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )


@reports_router.get("/divergences/{questionnaire_id}")
async def get_divergences(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener divergencias de un cuestionario"""
    from .services.divergence import DivergenceService
    service = DivergenceService(db)
    return {
        "alerts": service.get_divergence_alerts(questionnaire_id),
        "summary": service.get_divergence_summary(questionnaire_id)
    }


app.include_router(reports_router, prefix="/api")


# SMTP Config Router
from .models import SMTPConfig
from .schemas import SMTPConfigCreate, SMTPConfigUpdate, SMTPConfigResponse
from .utils.security import encrypt_password, decrypt_password

smtp_router = APIRouter(prefix="/smtp", tags=["SMTP"])


@smtp_router.get("/{company_id}", response_model=SMTPConfigResponse)
async def get_smtp_config(
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener configuración SMTP de una empresa"""
    config = db.query(SMTPConfig).filter(SMTPConfig.company_id == company_id).first()
    if not config:
        return JSONResponse(status_code=404, content={"detail": "Configuración no encontrada"})
    return config


@smtp_router.post("/{company_id}", response_model=SMTPConfigResponse)
async def create_smtp_config(
    company_id: int,
    data: SMTPConfigCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear configuración SMTP para una empresa"""
    existing = db.query(SMTPConfig).filter(SMTPConfig.company_id == company_id).first()
    if existing:
        return JSONResponse(status_code=400, content={"detail": "Ya existe configuración SMTP"})
    
    config_data = data.model_dump()
    if config_data.get("password"):
        config_data["password_encrypted"] = encrypt_password(config_data.pop("password"))
    else:
        config_data.pop("password", None)
    
    config = SMTPConfig(company_id=company_id, **config_data)
    db.add(config)
    db.commit()
    db.refresh(config)
    
    return config


@smtp_router.put("/{company_id}", response_model=SMTPConfigResponse)
async def update_smtp_config(
    company_id: int,
    data: SMTPConfigUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Actualizar configuración SMTP"""
    config = db.query(SMTPConfig).filter(SMTPConfig.company_id == company_id).first()
    if not config:
        return JSONResponse(status_code=404, content={"detail": "Configuración no encontrada"})
    
    update_data = data.model_dump(exclude_unset=True)
    if "password" in update_data and update_data["password"]:
        config.password_encrypted = encrypt_password(update_data.pop("password"))
    else:
        update_data.pop("password", None)
    
    for key, value in update_data.items():
        setattr(config, key, value)
    
    db.commit()
    db.refresh(config)
    
    return config


@smtp_router.post("/{company_id}/test")
async def test_smtp_config(
    company_id: int,
    test_email: str,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Probar configuración SMTP enviando un correo de prueba"""
    from .utils.email import EmailService
    
    config = db.query(SMTPConfig).filter(SMTPConfig.company_id == company_id).first()
    if not config:
        return JSONResponse(status_code=404, content={"detail": "Configuración no encontrada"})
    
    email_service = EmailService(config)
    success = email_service.send_email(
        to_email=test_email,
        subject="[CyberGAP] Prueba de Configuración SMTP",
        html_content="<h1>Prueba exitosa</h1><p>La configuración SMTP funciona correctamente.</p>",
        text_content="Prueba exitosa. La configuración SMTP funciona correctamente."
    )
    
    return {
        "success": success,
        "message": "Correo enviado correctamente" if success else "Error al enviar correo"
    }


app.include_router(smtp_router, prefix="/api")


# Root redirect to docs
@app.get("/")
async def root():
    """Redirigir a documentación"""
    from fastapi.responses import RedirectResponse
    return RedirectResponse(url="/api/docs")


# Static files for frontend (production)
static_path = os.path.join(os.path.dirname(__file__), "..", "..", "frontend", "dist")
if os.path.exists(static_path):
    app.mount("/", StaticFiles(directory=static_path, html=True), name="static")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=int(os.getenv("PORT", 8000)),
        reload=os.getenv("DEBUG", "false").lower() == "true"
    )
