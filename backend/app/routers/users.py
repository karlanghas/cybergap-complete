"""
Router de Usuarios
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import User, Area, Company, AdminUser
from ..schemas import UserCreate, UserUpdate, UserResponse, UserWithArea
from .auth import get_current_admin

router = APIRouter(prefix="/users", tags=["Usuarios"])


@router.get("", response_model=List[UserWithArea])
async def list_users(
    company_id: Optional[int] = None,
    area_id: Optional[int] = None,
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Listar usuarios con filtros"""
    query = db.query(User).join(Area).join(Company)
    
    if company_id:
        query = query.filter(Company.id == company_id)
    
    if area_id:
        query = query.filter(User.area_id == area_id)
    
    if search:
        query = query.filter(
            (User.full_name.ilike(f"%{search}%")) |
            (User.email.ilike(f"%{search}%"))
        )
    
    if is_active is not None:
        query = query.filter(User.is_active == is_active)
    
    users = query.order_by(User.full_name).offset(skip).limit(limit).all()
    
    result = []
    for user in users:
        area = db.query(Area).filter(Area.id == user.area_id).first()
        company = db.query(Company).filter(Company.id == area.company_id).first() if area else None
        
        result.append(UserWithArea(
            id=user.id,
            email=user.email,
            full_name=user.full_name,
            position=user.position,
            phone=user.phone,
            area_id=user.area_id,
            is_active=user.is_active,
            created_at=user.created_at,
            updated_at=user.updated_at,
            area_name=area.name if area else "",
            company_id=company.id if company else 0,
            company_name=company.name if company else ""
        ))
    
    return result


@router.post("", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear nuevo usuario"""
    # Verificar que el área existe
    area = db.query(Area).filter(Area.id == user_data.area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    
    # Verificar email único en el área
    existing = db.query(User).filter(
        User.email == user_data.email,
        User.area_id == user_data.area_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con ese email en esta área"
        )
    
    user = User(**user_data.model_dump())
    db.add(user)
    db.commit()
    db.refresh(user)
    
    return user


@router.post("/bulk", response_model=List[UserResponse], status_code=status.HTTP_201_CREATED)
async def create_users_bulk(
    users_data: List[UserCreate],
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear múltiples usuarios"""
    created_users = []
    errors = []
    
    for i, user_data in enumerate(users_data):
        try:
            # Verificar área
            area = db.query(Area).filter(Area.id == user_data.area_id).first()
            if not area:
                errors.append(f"Fila {i+1}: Área no encontrada")
                continue
            
            # Verificar duplicado
            existing = db.query(User).filter(
                User.email == user_data.email,
                User.area_id == user_data.area_id
            ).first()
            if existing:
                errors.append(f"Fila {i+1}: Email duplicado en el área")
                continue
            
            user = User(**user_data.model_dump())
            db.add(user)
            created_users.append(user)
            
        except Exception as e:
            errors.append(f"Fila {i+1}: {str(e)}")
    
    if created_users:
        db.commit()
        for user in created_users:
            db.refresh(user)
    
    if errors:
        # Si hay errores pero también usuarios creados, devolver parcial
        if created_users:
            return created_users
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"errors": errors}
        )
    
    return created_users


@router.get("/{user_id}", response_model=UserWithArea)
async def get_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener usuario por ID"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    area = db.query(Area).filter(Area.id == user.area_id).first()
    company = db.query(Company).filter(Company.id == area.company_id).first() if area else None
    
    return UserWithArea(
        id=user.id,
        email=user.email,
        full_name=user.full_name,
        position=user.position,
        phone=user.phone,
        area_id=user.area_id,
        is_active=user.is_active,
        created_at=user.created_at,
        updated_at=user.updated_at,
        area_name=area.name if area else "",
        company_id=company.id if company else 0,
        company_name=company.name if company else ""
    )


@router.put("/{user_id}", response_model=UserResponse)
async def update_user(
    user_id: int,
    user_data: UserUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Actualizar usuario"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    update_data = user_data.model_dump(exclude_unset=True)
    
    # Verificar área si se cambia
    if "area_id" in update_data:
        area = db.query(Area).filter(Area.id == update_data["area_id"]).first()
        if not area:
            raise HTTPException(status_code=404, detail="Área no encontrada")
    
    # Verificar email único si se cambia
    if "email" in update_data:
        area_id = update_data.get("area_id", user.area_id)
        existing = db.query(User).filter(
            User.email == update_data["email"],
            User.area_id == area_id,
            User.id != user_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe un usuario con ese email en el área"
            )
    
    for key, value in update_data.items():
        setattr(user, key, value)
    
    db.commit()
    db.refresh(user)
    
    return user


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Eliminar usuario (soft delete)"""
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    user.is_active = False
    db.commit()
