"""
Router de Autenticación
"""
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import AdminUser
from ..schemas import Token, LoginRequest, AdminUserCreate, AdminUserResponse, AdminUserUpdate
from ..utils.security import verify_password, get_password_hash, create_access_token, decode_token

router = APIRouter(prefix="/auth", tags=["Autenticación"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")


async def get_current_admin(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
) -> AdminUser:
    """Obtener admin actual desde token"""
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudo validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    payload = decode_token(token)
    if payload is None:
        raise credentials_exception
    
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    admin = db.query(AdminUser).filter(AdminUser.email == email).first()
    if admin is None or not admin.is_active:
        raise credentials_exception
    
    return admin


async def get_current_superadmin(
    admin: AdminUser = Depends(get_current_admin)
) -> AdminUser:
    """Verificar que el admin es superadmin"""
    if not admin.is_superadmin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Se requiere permisos de superadministrador"
        )
    return admin


@router.post("/token", response_model=Token)
async def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db)
):
    """Endpoint OAuth2 para login"""
    admin = db.query(AdminUser).filter(AdminUser.email == form_data.username).first()
    
    if not admin or not verify_password(form_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado"
        )
    
    # Actualizar último login
    admin.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(data={"sub": admin.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
async def login_json(
    login_data: LoginRequest,
    db: Session = Depends(get_db)
):
    """Login con JSON body"""
    admin = db.query(AdminUser).filter(AdminUser.email == login_data.email).first()
    
    if not admin or not verify_password(login_data.password, admin.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos"
        )
    
    if not admin.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuario desactivado"
        )
    
    admin.last_login = datetime.utcnow()
    db.commit()
    
    access_token = create_access_token(data={"sub": admin.email})
    
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/me", response_model=AdminUserResponse)
async def get_me(admin: AdminUser = Depends(get_current_admin)):
    """Obtener información del admin actual"""
    return admin


@router.post("/admins", response_model=AdminUserResponse)
async def create_admin(
    admin_data: AdminUserCreate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin)
):
    """Crear nuevo administrador (solo superadmin)"""
    # Verificar email único
    existing = db.query(AdminUser).filter(AdminUser.email == admin_data.email).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado"
        )
    
    admin = AdminUser(
        email=admin_data.email,
        full_name=admin_data.full_name,
        hashed_password=get_password_hash(admin_data.password),
        is_superadmin=admin_data.is_superadmin
    )
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    return admin


@router.put("/admins/{admin_id}", response_model=AdminUserResponse)
async def update_admin(
    admin_id: int,
    admin_data: AdminUserUpdate,
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin)
):
    """Actualizar administrador"""
    admin = db.query(AdminUser).filter(AdminUser.id == admin_id).first()
    if not admin:
        raise HTTPException(status_code=404, detail="Administrador no encontrado")
    
    update_data = admin_data.model_dump(exclude_unset=True)
    
    if "password" in update_data:
        update_data["hashed_password"] = get_password_hash(update_data.pop("password"))
    
    for key, value in update_data.items():
        setattr(admin, key, value)
    
    db.commit()
    db.refresh(admin)
    
    return admin


@router.get("/admins", response_model=list[AdminUserResponse])
async def list_admins(
    db: Session = Depends(get_db),
    current_admin: AdminUser = Depends(get_current_superadmin)
):
    """Listar todos los administradores"""
    return db.query(AdminUser).all()
