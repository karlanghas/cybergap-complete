"""
Router Público - Responder Cuestionarios
Este endpoint NO requiere autenticación de admin
"""
from typing import List, Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.orm import Session

from ..database import get_db
from ..models import (
    AccessToken, TokenStatus, QuestionAssignment, Question, 
    User, Area, Company, QuestionnaireAssignment, Response
)
from ..schemas import (
    PublicQuestionnaire, PublicQuestionnaireInfo, PublicQuestion,
    ResponseSubmit, QuestionOption
)
from ..services.divergence import DivergenceService

router = APIRouter(prefix="/public", tags=["Público"])


@router.get("/survey/{token}", response_model=PublicQuestionnaire)
async def get_survey(
    token: str,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Obtener cuestionario público por token
    Valida el token y devuelve las preguntas asignadas al usuario
    """
    # Buscar token
    access_token = db.query(AccessToken).filter(AccessToken.token == token).first()
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enlace inválido o expirado"
        )
    
    # Verificar estado del token
    if access_token.status == TokenStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este cuestionario ya fue completado"
        )
    
    if access_token.status == TokenStatus.EXPIRED:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este enlace ha expirado"
        )
    
    # Verificar fecha de expiración
    if access_token.expires_at and access_token.expires_at < datetime.utcnow():
        access_token.status = TokenStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este enlace ha expirado"
        )
    
    # Marcar como abierto
    if access_token.status in [TokenStatus.PENDING, TokenStatus.SENT]:
        access_token.status = TokenStatus.OPENED
        access_token.opened_at = datetime.utcnow()
        access_token.ip_address = request.client.host if request.client else None
        access_token.user_agent = request.headers.get("user-agent", "")[:500]
        db.commit()
    
    # Obtener datos
    user = db.query(User).filter(User.id == access_token.user_id).first()
    questionnaire = db.query(QuestionnaireAssignment).filter(
        QuestionnaireAssignment.id == access_token.questionnaire_id
    ).first()
    company = db.query(Company).filter(Company.id == questionnaire.company_id).first()
    
    # Obtener asignaciones del usuario para este cuestionario
    assignments = db.query(QuestionAssignment).filter(
        QuestionAssignment.questionnaire_id == access_token.questionnaire_id,
        QuestionAssignment.user_id == access_token.user_id
    ).order_by(QuestionAssignment.order).all()
    
    # Filtrar las que ya tienen respuesta
    questions = []
    for assignment in assignments:
        # Verificar si ya tiene respuesta
        existing_response = db.query(Response).filter(
            Response.assignment_id == assignment.id
        ).first()
        
        if existing_response:
            continue  # Ya respondida
        
        question = db.query(Question).filter(Question.id == assignment.question_id).first()
        if question and question.is_active:
            options = None
            if question.options:
                options = [
                    QuestionOption(
                        value=opt.get("value", ""),
                        text=opt.get("text", ""),
                        score=opt.get("score", 0)
                    )
                    for opt in question.options
                ]
            
            questions.append(PublicQuestion(
                assignment_id=assignment.id,
                question_id=question.id,
                text=question.text,
                description=question.description,
                question_type=question.question_type,
                options=options,
                required=question.required,
                order=assignment.order
            ))
    
    # Si no hay preguntas pendientes, marcar como completado
    if not questions:
        access_token.status = TokenStatus.COMPLETED
        access_token.completed_at = datetime.utcnow()
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Ya has completado todas las preguntas de este cuestionario"
        )
    
    return PublicQuestionnaire(
        info=PublicQuestionnaireInfo(
            questionnaire_name=questionnaire.name,
            company_name=company.name,
            company_logo=company.logo_url,
            user_name=user.full_name,
            total_questions=len(questions),
            deadline=questionnaire.end_date
        ),
        questions=questions
    )


@router.post("/survey/{token}/submit", response_model=dict)
async def submit_survey(
    token: str,
    data: ResponseSubmit,
    request: Request,
    db: Session = Depends(get_db)
):
    """
    Enviar respuestas del cuestionario
    Este endpoint marca el token como usado después de un envío exitoso
    """
    # Validar token
    access_token = db.query(AccessToken).filter(AccessToken.token == token).first()
    
    if not access_token:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Enlace inválido"
        )
    
    if access_token.status == TokenStatus.COMPLETED:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este cuestionario ya fue completado"
        )
    
    if access_token.status == TokenStatus.EXPIRED:
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este enlace ha expirado"
        )
    
    # Verificar fecha de expiración
    if access_token.expires_at and access_token.expires_at < datetime.utcnow():
        access_token.status = TokenStatus.EXPIRED
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_410_GONE,
            detail="Este enlace ha expirado"
        )
    
    # Procesar respuestas
    saved_count = 0
    errors = []
    
    for resp_data in data.responses:
        assignment_id = resp_data.get("assignment_id")
        answer = resp_data.get("answer")
        time_spent = resp_data.get("time_spent_seconds", 0)
        
        # Verificar que la asignación pertenece al usuario y cuestionario
        assignment = db.query(QuestionAssignment).filter(
            QuestionAssignment.id == assignment_id,
            QuestionAssignment.questionnaire_id == access_token.questionnaire_id,
            QuestionAssignment.user_id == access_token.user_id
        ).first()
        
        if not assignment:
            errors.append(f"Asignación {assignment_id} no válida")
            continue
        
        # Verificar si ya existe respuesta
        existing = db.query(Response).filter(Response.assignment_id == assignment_id).first()
        if existing:
            errors.append(f"Pregunta {assignment_id} ya respondida")
            continue
        
        # Calcular score
        question = db.query(Question).filter(Question.id == assignment.question_id).first()
        score = calculate_score(question, answer)
        
        # Guardar respuesta
        response = Response(
            assignment_id=assignment_id,
            answer=answer,
            score=score,
            time_spent_seconds=time_spent
        )
        db.add(response)
        saved_count += 1
    
    # Verificar si quedan preguntas pendientes
    total_assignments = db.query(QuestionAssignment).filter(
        QuestionAssignment.questionnaire_id == access_token.questionnaire_id,
        QuestionAssignment.user_id == access_token.user_id
    ).count()
    
    total_responses = db.query(Response).join(QuestionAssignment).filter(
        QuestionAssignment.questionnaire_id == access_token.questionnaire_id,
        QuestionAssignment.user_id == access_token.user_id
    ).count() + saved_count
    
    # Si todas las preguntas están respondidas, marcar token como completado
    if total_responses >= total_assignments:
        access_token.status = TokenStatus.COMPLETED
        access_token.completed_at = datetime.utcnow()
        
        # Recalcular divergencias en background
        try:
            service = DivergenceService(db)
            service.calculate_divergences(access_token.questionnaire_id)
        except Exception as e:
            pass  # No fallar si hay error calculando divergencias
    
    db.commit()
    
    return {
        "success": True,
        "saved": saved_count,
        "errors": errors,
        "completed": access_token.status == TokenStatus.COMPLETED,
        "message": "Respuestas guardadas correctamente" if saved_count > 0 else "No se guardaron respuestas"
    }


def calculate_score(question: Question, answer) -> float:
    """Calcular puntaje basado en la respuesta"""
    if not question or answer is None:
        return 0
    
    if question.question_type.value == "yes_no":
        # Asumimos que "yes" es la respuesta correcta/deseada
        return question.max_score if str(answer).lower() in ["yes", "sí", "si", "true", "1"] else 0
    
    elif question.question_type.value == "single_choice":
        if question.options:
            for opt in question.options:
                if str(opt.get("value")) == str(answer):
                    return opt.get("score", 0)
        return 0
    
    elif question.question_type.value == "multiple_choice":
        total_score = 0
        if question.options and isinstance(answer, list):
            for opt in question.options:
                if opt.get("value") in answer:
                    total_score += opt.get("score", 0)
        return total_score
    
    elif question.question_type.value == "scale":
        # Para escala, el score es proporcional al valor
        try:
            value = float(answer)
            # Asumiendo escala 1-5 o 1-10
            max_scale = 10 if question.max_score > 50 else 5
            return (value / max_scale) * question.max_score
        except (ValueError, TypeError):
            return 0
    
    elif question.question_type.value == "text":
        # Para texto, asignar score completo si hay respuesta
        return question.max_score if answer and str(answer).strip() else 0
    
    return 0


@router.get("/survey/{token}/status", response_model=dict)
async def get_survey_status(
    token: str,
    db: Session = Depends(get_db)
):
    """Obtener estado del cuestionario"""
    access_token = db.query(AccessToken).filter(AccessToken.token == token).first()
    
    if not access_token:
        return {"valid": False, "status": "invalid"}
    
    return {
        "valid": True,
        "status": access_token.status.value,
        "sent_at": access_token.sent_at.isoformat() if access_token.sent_at else None,
        "opened_at": access_token.opened_at.isoformat() if access_token.opened_at else None,
        "completed_at": access_token.completed_at.isoformat() if access_token.completed_at else None,
        "expires_at": access_token.expires_at.isoformat() if access_token.expires_at else None
    }
