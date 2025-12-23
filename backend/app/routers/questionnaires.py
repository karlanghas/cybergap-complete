"""
Router de Cuestionarios y Asignaciones
"""
from typing import List, Optional
from datetime import datetime, timedelta
from fastapi import APIRouter, Depends, HTTPException, status, Query, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func

from ..database import get_db
from ..models import (
    QuestionnaireAssignment, QuestionAssignment, Question, User, Area, 
    Company, AccessToken, TokenStatus, Response, AdminUser, SMTPConfig
)
from ..schemas import (
    QuestionnaireAssignmentCreate, QuestionnaireAssignmentUpdate, 
    QuestionnaireAssignmentResponse, QuestionnaireWithStats,
    QuestionAssignmentCreate, QuestionAssignmentBulkCreate, 
    QuestionAssignmentResponse, QuestionAssignmentWithDetails,
    SendTokensRequest, AccessTokenResponse
)
from ..utils.security import generate_unique_token
from ..utils.email import EmailService, get_questionnaire_email_template
from ..services.divergence import DivergenceService
from .auth import get_current_admin

router = APIRouter(prefix="/questionnaires", tags=["Cuestionarios"])


@router.get("", response_model=List[QuestionnaireWithStats])
async def list_questionnaires(
    company_id: Optional[int] = None,
    is_active: Optional[bool] = None,
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Listar cuestionarios con estadísticas"""
    query = db.query(QuestionnaireAssignment)
    
    if company_id:
        query = query.filter(QuestionnaireAssignment.company_id == company_id)
    
    if is_active is not None:
        query = query.filter(QuestionnaireAssignment.is_active == is_active)
    
    questionnaires = query.order_by(QuestionnaireAssignment.created_at.desc()).offset(skip).limit(limit).all()
    
    result = []
    for q in questionnaires:
        company = db.query(Company).filter(Company.id == q.company_id).first()
        
        total_assignments = db.query(QuestionAssignment).filter(
            QuestionAssignment.questionnaire_id == q.id
        ).count()
        
        completed_assignments = db.query(QuestionAssignment).join(Response).filter(
            QuestionAssignment.questionnaire_id == q.id
        ).count()
        
        divergence_count = db.query(func.count()).filter(
            QuestionnaireAssignment.id == q.id
        ).scalar() or 0
        
        completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
        
        result.append(QuestionnaireWithStats(
            id=q.id,
            company_id=q.company_id,
            name=q.name,
            description=q.description,
            start_date=q.start_date,
            end_date=q.end_date,
            is_active=q.is_active,
            send_reminders=q.send_reminders,
            reminder_days=q.reminder_days,
            created_at=q.created_at,
            updated_at=q.updated_at,
            company_name=company.name if company else "",
            total_assignments=total_assignments,
            completed_assignments=completed_assignments,
            completion_rate=round(completion_rate, 2),
            divergence_alerts_count=divergence_count
        ))
    
    return result


@router.post("", response_model=QuestionnaireAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_questionnaire(
    data: QuestionnaireAssignmentCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear nuevo cuestionario/campaña"""
    # Verificar empresa
    company = db.query(Company).filter(Company.id == data.company_id).first()
    if not company:
        raise HTTPException(status_code=404, detail="Empresa no encontrada")
    
    questionnaire = QuestionnaireAssignment(**data.model_dump())
    db.add(questionnaire)
    db.commit()
    db.refresh(questionnaire)
    
    return questionnaire


@router.get("/{questionnaire_id}", response_model=QuestionnaireWithStats)
async def get_questionnaire(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Obtener cuestionario por ID"""
    q = db.query(QuestionnaireAssignment).filter(QuestionnaireAssignment.id == questionnaire_id).first()
    if not q:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    company = db.query(Company).filter(Company.id == q.company_id).first()
    
    total_assignments = db.query(QuestionAssignment).filter(
        QuestionAssignment.questionnaire_id == q.id
    ).count()
    
    completed_assignments = db.query(QuestionAssignment).join(Response).filter(
        QuestionAssignment.questionnaire_id == q.id
    ).count()
    
    completion_rate = (completed_assignments / total_assignments * 100) if total_assignments > 0 else 0
    
    return QuestionnaireWithStats(
        id=q.id,
        company_id=q.company_id,
        name=q.name,
        description=q.description,
        start_date=q.start_date,
        end_date=q.end_date,
        is_active=q.is_active,
        send_reminders=q.send_reminders,
        reminder_days=q.reminder_days,
        created_at=q.created_at,
        updated_at=q.updated_at,
        company_name=company.name if company else "",
        total_assignments=total_assignments,
        completed_assignments=completed_assignments,
        completion_rate=round(completion_rate, 2),
        divergence_alerts_count=0
    )


@router.put("/{questionnaire_id}", response_model=QuestionnaireAssignmentResponse)
async def update_questionnaire(
    questionnaire_id: int,
    data: QuestionnaireAssignmentUpdate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Actualizar cuestionario"""
    questionnaire = db.query(QuestionnaireAssignment).filter(
        QuestionnaireAssignment.id == questionnaire_id
    ).first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    update_data = data.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(questionnaire, key, value)
    
    db.commit()
    db.refresh(questionnaire)
    
    return questionnaire


@router.delete("/{questionnaire_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_questionnaire(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Eliminar cuestionario (soft delete)"""
    questionnaire = db.query(QuestionnaireAssignment).filter(
        QuestionnaireAssignment.id == questionnaire_id
    ).first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    questionnaire.is_active = False
    db.commit()


# ============================================================================
# ASIGNACIONES DE PREGUNTAS
# ============================================================================

@router.get("/{questionnaire_id}/assignments", response_model=List[QuestionAssignmentWithDetails])
async def list_assignments(
    questionnaire_id: int,
    user_id: Optional[int] = None,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Listar asignaciones de un cuestionario"""
    query = db.query(QuestionAssignment).filter(
        QuestionAssignment.questionnaire_id == questionnaire_id
    )
    
    if user_id:
        query = query.filter(QuestionAssignment.user_id == user_id)
    
    assignments = query.order_by(QuestionAssignment.order).all()
    
    result = []
    for a in assignments:
        question = db.query(Question).filter(Question.id == a.question_id).first()
        user = db.query(User).filter(User.id == a.user_id).first()
        area = db.query(Area).filter(Area.id == user.area_id).first() if user else None
        response = db.query(Response).filter(Response.assignment_id == a.id).first()
        
        result.append(QuestionAssignmentWithDetails(
            id=a.id,
            questionnaire_id=a.questionnaire_id,
            question_id=a.question_id,
            user_id=a.user_id,
            order=a.order,
            is_mandatory=a.is_mandatory,
            created_at=a.created_at,
            question_text=question.text if question else "",
            question_type=question.question_type if question else "text",
            user_name=user.full_name if user else "",
            user_email=user.email if user else "",
            area_name=area.name if area else "",
            is_answered=response is not None
        ))
    
    return result


@router.post("/{questionnaire_id}/assignments", response_model=QuestionAssignmentResponse, status_code=status.HTTP_201_CREATED)
async def create_assignment(
    questionnaire_id: int,
    data: QuestionAssignmentCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear asignación individual"""
    # Verificar cuestionario
    questionnaire = db.query(QuestionnaireAssignment).filter(
        QuestionnaireAssignment.id == questionnaire_id
    ).first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    # Verificar pregunta
    question = db.query(Question).filter(Question.id == data.question_id).first()
    if not question:
        raise HTTPException(status_code=404, detail="Pregunta no encontrada")
    
    # Verificar usuario
    user = db.query(User).filter(User.id == data.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    
    # Verificar que el usuario pertenece a la empresa del cuestionario
    area = db.query(Area).filter(Area.id == user.area_id).first()
    if area.company_id != questionnaire.company_id:
        raise HTTPException(
            status_code=400,
            detail="El usuario no pertenece a la empresa del cuestionario"
        )
    
    # Verificar duplicado
    existing = db.query(QuestionAssignment).filter(
        QuestionAssignment.questionnaire_id == questionnaire_id,
        QuestionAssignment.question_id == data.question_id,
        QuestionAssignment.user_id == data.user_id
    ).first()
    if existing:
        raise HTTPException(
            status_code=400,
            detail="Ya existe esta asignación"
        )
    
    assignment = QuestionAssignment(
        questionnaire_id=questionnaire_id,
        question_id=data.question_id,
        user_id=data.user_id,
        order=data.order,
        is_mandatory=data.is_mandatory
    )
    db.add(assignment)
    db.commit()
    db.refresh(assignment)
    
    return assignment


@router.post("/{questionnaire_id}/assignments/bulk", response_model=List[QuestionAssignmentResponse], status_code=status.HTTP_201_CREATED)
async def create_assignments_bulk(
    questionnaire_id: int,
    data: QuestionAssignmentBulkCreate,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Crear múltiples asignaciones"""
    questionnaire = db.query(QuestionnaireAssignment).filter(
        QuestionnaireAssignment.id == questionnaire_id
    ).first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    created = []
    for item in data.assignments:
        # Verificar que no existe
        existing = db.query(QuestionAssignment).filter(
            QuestionAssignment.questionnaire_id == questionnaire_id,
            QuestionAssignment.question_id == item["question_id"],
            QuestionAssignment.user_id == item["user_id"]
        ).first()
        
        if not existing:
            assignment = QuestionAssignment(
                questionnaire_id=questionnaire_id,
                question_id=item["question_id"],
                user_id=item["user_id"],
                order=len(created)
            )
            db.add(assignment)
            created.append(assignment)
    
    db.commit()
    for a in created:
        db.refresh(a)
    
    return created


@router.delete("/{questionnaire_id}/assignments/{assignment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_assignment(
    questionnaire_id: int,
    assignment_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Eliminar asignación"""
    assignment = db.query(QuestionAssignment).filter(
        QuestionAssignment.id == assignment_id,
        QuestionAssignment.questionnaire_id == questionnaire_id
    ).first()
    if not assignment:
        raise HTTPException(status_code=404, detail="Asignación no encontrada")
    
    # Verificar si ya tiene respuesta
    response = db.query(Response).filter(Response.assignment_id == assignment_id).first()
    if response:
        raise HTTPException(
            status_code=400,
            detail="No se puede eliminar una asignación con respuesta"
        )
    
    db.delete(assignment)
    db.commit()


# ============================================================================
# TOKENS Y ENVÍO DE EMAILS
# ============================================================================

@router.post("/{questionnaire_id}/send-tokens", response_model=dict)
async def send_tokens(
    questionnaire_id: int,
    data: SendTokensRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Generar y enviar tokens a usuarios"""
    questionnaire = db.query(QuestionnaireAssignment).filter(
        QuestionnaireAssignment.id == questionnaire_id
    ).first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    company = db.query(Company).filter(Company.id == questionnaire.company_id).first()
    
    # Obtener configuración SMTP de la empresa o usar default
    smtp_config = db.query(SMTPConfig).filter(
        SMTPConfig.company_id == questionnaire.company_id,
        SMTPConfig.is_active == True
    ).first()
    
    email_service = EmailService(smtp_config)
    
    # Obtener usuarios a enviar
    if data.user_ids:
        user_ids = data.user_ids
    else:
        # Obtener todos los usuarios con asignaciones
        user_ids = db.query(QuestionAssignment.user_id).filter(
            QuestionAssignment.questionnaire_id == questionnaire_id
        ).distinct().all()
        user_ids = [u[0] for u in user_ids]
    
    sent_count = 0
    error_count = 0
    
    for user_id in user_ids:
        user = db.query(User).filter(User.id == user_id).first()
        if not user or not user.is_active:
            continue
        
        # Verificar si ya tiene token activo
        existing_token = db.query(AccessToken).filter(
            AccessToken.user_id == user_id,
            AccessToken.questionnaire_id == questionnaire_id,
            AccessToken.status.in_([TokenStatus.PENDING, TokenStatus.SENT, TokenStatus.OPENED])
        ).first()
        
        if existing_token and existing_token.status == TokenStatus.COMPLETED:
            continue  # Ya completó
        
        # Generar o reusar token
        if not existing_token:
            token_str = generate_unique_token()
            access_token = AccessToken(
                user_id=user_id,
                questionnaire_id=questionnaire_id,
                token=token_str,
                status=TokenStatus.PENDING,
                expires_at=questionnaire.end_date
            )
            db.add(access_token)
        else:
            token_str = existing_token.token
            access_token = existing_token
        
        # Enviar email
        html_content, text_content = get_questionnaire_email_template(
            user_name=user.full_name,
            company_name=company.name,
            questionnaire_name=questionnaire.name,
            token=token_str,
            deadline=questionnaire.end_date
        )
        
        success = email_service.send_email(
            to_email=user.email,
            subject=f"[{company.name}] Cuestionario de Cumplimiento - {questionnaire.name}",
            html_content=html_content,
            text_content=text_content
        )
        
        if success:
            access_token.status = TokenStatus.SENT
            access_token.sent_at = datetime.utcnow()
            sent_count += 1
        else:
            error_count += 1
    
    db.commit()
    
    return {
        "sent": sent_count,
        "errors": error_count,
        "message": f"Se enviaron {sent_count} correos exitosamente"
    }


@router.get("/{questionnaire_id}/tokens", response_model=List[AccessTokenResponse])
async def list_tokens(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Listar tokens de un cuestionario"""
    tokens = db.query(AccessToken).filter(
        AccessToken.questionnaire_id == questionnaire_id
    ).all()
    
    return tokens


# ============================================================================
# DIVERGENCIAS
# ============================================================================

@router.post("/{questionnaire_id}/calculate-divergences", response_model=dict)
async def calculate_divergences(
    questionnaire_id: int,
    db: Session = Depends(get_db),
    admin: AdminUser = Depends(get_current_admin)
):
    """Calcular divergencias para un cuestionario"""
    questionnaire = db.query(QuestionnaireAssignment).filter(
        QuestionnaireAssignment.id == questionnaire_id
    ).first()
    if not questionnaire:
        raise HTTPException(status_code=404, detail="Cuestionario no encontrado")
    
    service = DivergenceService(db)
    alerts = service.calculate_divergences(questionnaire_id)
    summary = service.get_divergence_summary(questionnaire_id)
    
    return {
        "alerts_created": len(alerts),
        "summary": summary
    }
