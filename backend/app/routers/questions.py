"""
Router de Preguntas y Categorías
"""
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import Question, Category, AdminUser
from ..schemas import (
    QuestionCreate, QuestionUpdate, QuestionResponse, QuestionWithCategory,
    CategoryCreate, CategoryUpdate, CategoryResponse, CategoryWithCount
)
from .auth import get_current_admin

router = APIRouter(prefix="/questions", tags=["Preguntas"])
category_router = APIRouter(prefix="/categories", tags=["Categorías"])


# ============================================================================
# CATEGORÍAS
# ============================================================================

@category_router.get("", response_model=List[CategoryWithCount])
async def list_categories(
    is_active: Optional[bool] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Listar categorías con conteo de preguntas"""
    query = db.query(Category)
    
    if is_active is not None:
        query = query.filter(Category.is_active == is_active)
    
    categories = query.order_by(Category.order, Category.name).all()
    
    result = []
    for cat in categories:
        questions_count = db.query(Question).filter(
            Question.category_id == cat.id,
            Question.is_active == True
        ).count()
        
        result.append(CategoryWithCount(
            id=cat.id,
            name=cat.name,
            code=cat.code,
            description=cat.description,
            color=cat.color,
            icon=cat.icon,
            order=cat.order,
            is_active=cat.is_active,
            created_at=cat.created_at,
            questions_count=questions_count
        ))
    
    return result


@category_router.post("", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_data: CategoryCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear nueva categoría"""
    existing = db.query(Category).filter(Category.name == category_data.name).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una categoría con ese nombre"
        )
    
    category = Category(**category_data.model_dump())
    db.add(category)
    db.commit()
    db.refresh(category)
    
    return category


@category_router.get("/{category_id}", response_model=CategoryWithCount)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener categoría por ID"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    questions_count = db.query(Question).filter(
        Question.category_id == category.id,
        Question.is_active == True
    ).count()
    
    return CategoryWithCount(
        id=category.id,
        name=category.name,
        code=category.code,
        description=category.description,
        color=category.color,
        icon=category.icon,
        order=category.order,
        is_active=category.is_active,
        created_at=category.created_at,
        questions_count=questions_count
    )


@category_router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_data: CategoryUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Actualizar categoría"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    update_data = category_data.model_dump(exclude_unset=True)
    
    if "name" in update_data:
        existing = db.query(Category).filter(
            Category.name == update_data["name"],
            Category.id != category_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una categoría con ese nombre"
            )
    
    for key, value in update_data.items():
        setattr(category, key, value)
    
    db.commit()
    db.refresh(category)
    
    return category


@category_router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Eliminar categoría (soft delete)"""
    category = db.query(Category).filter(Category.id == category_id).first()
    if not category:
        raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    category.is_active = False
    db.commit()


# ============================================================================
# PREGUNTAS
# ============================================================================

@router.get("", response_model=List[QuestionWithCategory])
async def list_questions(
    category_id: Optional[int] = None,
    question_type: Optional[str] = None,
    search: Optional[str] = None,
    tags: Optional[str] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Listar preguntas con filtros"""
    query = db.query(Question)
    
    if category_id:
        query = query.filter(Question.category_id == category_id)
    
    if question_type:
        query = query.filter(Question.question_type == question_type)
    
    if search:
        query = query.filter(
            (Question.text.ilike(f"%{search}%")) |
            (Question.code.ilike(f"%{search}%"))
        )
    
    if is_active is not None:
        query = query.filter(Question.is_active == is_active)
    
    questions = query.order_by(Question.order, Question.id).offset(skip).limit(limit).all()
    
    result = []
    for q in questions:
        category = db.query(Category).filter(Category.id == q.category_id).first() if q.category_id else None
        
        result.append(QuestionWithCategory(
            id=q.id,
            category_id=q.category_id,
            code=q.code,
            text=q.text,
            description=q.description,
            question_type=q.question_type,
            options=q.options,
            max_score=q.max_score,
            weight=q.weight,
            required=q.required,
            order=q.order,
            tags=q.tags,
            is_active=q.is_active,
            created_at=q.created_at,
            updated_at=q.updated_at,
            category_name=category.name if category else None,
            category_color=category.color if category else None
        ))
    
    return result


@router.post("", response_model=QuestionResponse, status_code=status.HTTP_201_CREATED)
async def create_question(
    question_data: QuestionCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear nueva pregunta"""
    # Verificar categoría si se especifica
    if question_data.category_id:
        category = db.query(Category).filter(Category.id == question_data.category_id).first()
        if not category:
            raise HTTPException(status_code=404, detail="Categoría no encontrada")
    
    # Verificar código único si se especifica
    if question_data.code:
        existing = db.query(Question).filter(Question.code == question_data.code).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una pregunta con ese código"
            )
    
    # Convertir options a dict si existe
    data = question_data.model_dump()
    if data.get("options"):
        data["options"] = [opt.model_dump() if hasattr(opt, "model_dump") else opt for opt in data["options"]]
    
    question = Question(**data)
    db.add(question)
    db.commit()
    db.refresh(question)
    
    return question


@router.post("/bulk", response_model=List[QuestionResponse], status_code=status.HTTP_201_CREATED)
async def create_questions_bulk(
    questions_data: List[QuestionCreate],
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear múltiples preguntas"""
    created_questions = []
    
    for question_data in questions_data:
        data = question_data.model_dump()
        if data.get("options"):
            data["options"] = [opt.model_dump() if hasattr(opt, "model_dump") else opt for opt in data["options"]]
        
        question = Question(**data)
        db.add(question)
        created_questions.append(question)
    
    db.commit()
    for q in created_questions:
        db.refresh(q)
    
    return created_questions


@router.get("/{question_id}", response_model=QuestionWithCategory)
async def get_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener pregunta por ID"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    category = db.query(Category).filter(Category.id == question.category_id).first() if question.category_id else None
    
    return QuestionWithCategory(
        id=question.id,
        category_id=question.category_id,
        code=question.code,
        text=question.text,
        description=question.description,
        question_type=question.question_type,
        options=question.options,
        max_score=question.max_score,
        weight=question.weight,
        required=question.required,
        order=question.order,
        tags=question.tags,
        is_active=question.is_active,
        created_at=question.created_at,
        updated_at=question.updated_at,
        category_name=category.name if category else None,
        category_color=category.color if category else None
    )


@router.put("/{question_id}", response_model=QuestionResponse)
async def update_question(
    question_id: int,
    question_data: QuestionUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Actualizar pregunta"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    update_data = question_data.model_dump(exclude_unset=True)
    
    # Verificar código único si se cambia
    if "code" in update_data and update_data["code"]:
        existing = db.query(Question).filter(
            Question.code == update_data["code"],
            Question.id != question_id
        ).first()
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Ya existe una pregunta con ese código"
            )
    
    # Convertir options si existe
    if "options" in update_data and update_data["options"]:
        update_data["options"] = [
            opt.model_dump() if hasattr(opt, "model_dump") else opt 
            for opt in update_data["options"]
        ]
    
    for key, value in update_data.items():
        setattr(question, key, value)
    
    db.commit()
    db.refresh(question)
    
    return question


@router.delete("/{question_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_question(
    question_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Eliminar pregunta (soft delete)"""
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    question.is_active = False
    db.commit()
