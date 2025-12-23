"""
Router de Áreas
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import Area, Company, User, AdminUser
from ..schemas import AreaCreate, AreaUpdate, AreaResponse, AreaWithChildren
from .auth import get_current_admin

router = APIRouter(prefix="/areas", tags=["Áreas"])


def build_area_tree(areas: List[Area], parent_id: Optional[int] = None) -> List[AreaWithChildren]:
    """Construir árbol jerárquico de áreas"""
    tree = []
    for area in areas:
        if area.parent_id == parent_id:
            children = build_area_tree(areas, area.id)
            users_count = len(area.users) if area.users else 0
            
            area_dict = AreaWithChildren(
                id=area.id,
                company_id=area.company_id,
                parent_id=area.parent_id,
                name=area.name,
                code=area.code,
                description=area.description,
                order=area.order,
                is_active=area.is_active,
                created_at=area.created_at,
                children=children,
                users_count=users_count
            )
            tree.append(area_dict)
    
    return sorted(tree, key=lambda x: x.order)


@router.get("", response_model=List[AreaResponse])
async def list_areas(
    company_id: Optional[int] = None,
    parent_id: Optional[int] = None,
    flat: bool = Query(True, description="Si es True, devuelve lista plana; si es False, devuelve árbol"),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Listar áreas"""
    query = db.query(Area).filter(Area.is_active == True)
    
    if company_id:
        query = query.filter(Area.company_id == company_id)
    
    if parent_id is not None:
        query = query.filter(Area.parent_id == parent_id)
    
    areas = query.order_by(Area.order, Area.name).all()
    
    return areas


@router.get("/tree/{company_id}", response_model=List[AreaWithChildren])
async def get_areas_tree(
    company_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener árbol jerárquico de áreas de una empresa"""
    areas = db.query(Area).filter(
        Area.company_id == company_id,
        Area.is_active == True
    ).all()
    
    return build_area_tree(areas)


@router.post("", response_model=AreaResponse, status_code=status.HTTP_201_CREATED)
async def create_area(
    area_data: AreaCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear nueva área"""
    # Verificar que la empresa existe
    company = db.query(Company).filter(Company.id == area_data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    # Verificar padre si se especifica
    if area_data.parent_id:
        parent = db.query(Area).filter(
            Area.id == area_data.parent_id,
            Area.company_id == area_data.company_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=400,
                detail="El área padre no existe o pertenece a otra empresa"
            )
    
    area = Area(**area_data.model_dump())
    db.add(area)
    db.commit()
    db.refresh(area)
    
    return area


@router.get("/{area_id}", response_model=AreaWithChildren)
async def get_area(
    area_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener área por ID"""
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    
    # Obtener hijos
    children_areas = db.query(Area).filter(
        Area.parent_id == area_id,
        Area.is_active == True
    ).all()
    
    children = build_area_tree(children_areas, area_id) if children_areas else []
    users_count = db.query(User).filter(User.area_id == area_id).count()
    
    return AreaWithChildren(
        id=area.id,
        company_id=area.company_id,
        parent_id=area.parent_id,
        name=area.name,
        code=area.code,
        description=area.description,
        order=area.order,
        is_active=area.is_active,
        created_at=area.created_at,
        children=children,
        users_count=users_count
    )


@router.put("/{area_id}", response_model=AreaResponse)
async def update_area(
    area_id: int,
    area_data: AreaUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Actualizar área"""
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    
    update_data = area_data.model_dump(exclude_unset=True)
    
    # Verificar padre si se cambia
    if "parent_id" in update_data and update_data["parent_id"]:
        # Evitar referencia circular
        if update_data["parent_id"] == area_id:
            raise HTTPException(
                status_code=400,
                detail="Un área no puede ser su propio padre"
            )
        
        parent = db.query(Area).filter(
            Area.id == update_data["parent_id"],
            Area.company_id == area.company_id
        ).first()
        if not parent:
            raise HTTPException(
                status_code=400,
                detail="El área padre no existe o pertenece a otra empresa"
            )
    
    for key, value in update_data.items():
        setattr(area, key, value)
    
    db.commit()
    db.refresh(area)
    
    return area


@router.delete("/{area_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_area(
    area_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Eliminar área (soft delete)"""
    area = db.query(Area).filter(Area.id == area_id).first()
    if not area:
        raise HTTPException(status_code=404, detail="Área no encontrada")
    
    # Verificar si tiene hijos
    children_count = db.query(Area).filter(Area.parent_id == area_id).count()
    if children_count > 0:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar un área con sub-áreas. Elimine primero las sub-áreas."
        )
    
    # Verificar si tiene usuarios
    users_count = db.query(User).filter(User.area_id == area_id).count()
    if users_count > 0:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar un área con usuarios. Reasigne o elimine los usuarios primero."
        )
    
    area.is_active = False
    db.commit()
