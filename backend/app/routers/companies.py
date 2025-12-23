"""
Router de Empresas (Companies)
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Company, Area, User, QuestionnaireAssignment, AdminUser
from ..schemas import (
    CompanyCreate, CompanyUpdate, CompanyResponse, CompanyWithStats
)
from .auth import get_current_admin

router = APIRouter(prefix="/companies", tags=["Empresas"])


@router.get("", response_model=List[CompanyWithStats])
async def list_companies(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    search: Optional[str] = None,
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Listar empresas con estadísticas"""
    query = db.query(Company)
    
    if search:
        query = query.filter(Company.name.ilike(f"%{search}%"))
    
    if is_active is not None:
        query = query.filter(Company.is_active == is_active)
    
    companies = query.order_by(Company.name).offset(skip).limit(limit).all()
    
    # Agregar estadísticas
    result = []
    for company in companies:
        areas_count = db.query(Area).filter(Area.company_id == company.id).count()
        users_count = db.query(User).join(Area).filter(Area.company_id == company.id).count()
        questionnaires_count = db.query(QuestionnaireAssignment).filter(
            QuestionnaireAssignment.company_id == company.id
        ).count()
        
        company_dict = {
            "id": company.id,
            "name": company.name,
            "rut": company.rut,
            "industry": company.industry,
            "logo_url": company.logo_url,
            "is_active": company.is_active,
            "created_at": company.created_at,
            "updated_at": company.updated_at,
            "areas_count": areas_count,
            "users_count": users_count,
            "questionnaires_count": questionnaires_count,
            "completion_rate": 0.0  # TODO: Calcular
        }
        result.append(CompanyWithStats(**company_dict))
    
    return result


@router.post("", response_model=CompanyResponse, status_code=status.HTTP_201_CREATED)
async def create_company(
    company_data: CompanyCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear nueva empresa"""
    # Verificar RUT único si se proporciona
    if company_data.rut:
        existing = db.query(Company).filter(Company.rut == company_data.rut).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una empresa con ese RUT"
            )
    
    company = Company(**company_data.model_dump())
    db.add(company)
    db.commit()
    db.refresh(company)
    
    return company


@router.get("/{company_id}", response_model=CompanyWithStats)
async def get_company(
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener empresa por ID"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    areas_count = db.query(Area).filter(Area.company_id == company.id).count()
    users_count = db.query(User).join(Area).filter(Area.company_id == company.id).count()
    questionnaires_count = db.query(QuestionnaireAssignment).filter(
        QuestionnaireAssignment.company_id == company.id
    ).count()
    
    return CompanyWithStats(
        id=company.id,
        name=company.name,
        rut=company.rut,
        industry=company.industry,
        logo_url=company.logo_url,
        is_active=company.is_active,
        created_at=company.created_at,
        updated_at=company.updated_at,
        areas_count=areas_count,
        users_count=users_count,
        questionnaires_count=questionnaires_count,
        completion_rate=0.0
    )


@router.put("/{company_id}", response_model=CompanyResponse)
async def update_company(
    company_id: int,
    company_data: CompanyUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Actualizar empresa"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    update_data = company_data.model_dump(exclude_unset=True)
    
    # Verificar RUT único si se cambia
    if "rut" in update_data and update_data["rut"]:
        existing = db.query(Company).filter(
            Company.rut == update_data["rut"],
            Company.id != company_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una empresa con ese RUT"
            )
    
    for key, value in update_data.items():
        setattr(company, key, value)
    
    db.commit()
    db.refresh(company)
    
    return company


@router.delete("/{company_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_company(
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Eliminar empresa (soft delete)"""
    company = db.query(Company).filter(Company.id == company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    company.is_active = False
    db.commit()
