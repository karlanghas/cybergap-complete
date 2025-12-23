"""
CyberGAP - Modelos de Base de Datos
Arquitectura Multi-Empresa con soporte para análisis de divergencias
"""
from datetime import datetime
from typing import Optional, List
from sqlalchemy import (
    Column, Integer, String, Text, Boolean, DateTime, Float,
    ForeignKey, Enum as SQLEnum, JSON, UniqueConstraint, Table
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()

# ============================================================================
# ENUMS
# ============================================================================

class QuestionType(str, enum.Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    SCALE = "scale"  # 1-5 o 1-10
    YES_NO = "yes_no"

class TokenStatus(str, enum.Enum):
    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"
    COMPLETED = "completed"
    EXPIRED = "expired"

class AlertSeverity(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

# ============================================================================
# MODELOS PRINCIPALES
# ============================================================================

class Company(Base):
    """Empresa/Cliente - Nivel superior de la jerarquía"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False)
    rut = Column(String(20), unique=True, nullable=True)  # Identificador fiscal
    industry = Column(String(100), nullable=True)
    logo_url = Column(String(500), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    areas = relationship("Area", back_populates="company", cascade="all, delete-orphan")
    smtp_config = relationship("SMTPConfig", back_populates="company", uselist=False, cascade="all, delete-orphan")
    questionnaire_assignments = relationship("QuestionnaireAssignment", back_populates="company", cascade="all, delete-orphan")


class Area(Base):
    """Áreas/Departamentos dentro de una empresa - Soporta jerarquía"""
    __tablename__ = "areas"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    parent_id = Column(Integer, ForeignKey("areas.id", ondelete="SET NULL"), nullable=True)
    name = Column(String(255), nullable=False)
    code = Column(String(50), nullable=True)  # Código interno
    description = Column(Text, nullable=True)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    company = relationship("Company", back_populates="areas")
    parent = relationship("Area", remote_side=[id], backref="children")
    users = relationship("User", back_populates="area", cascade="all, delete-orphan")


class User(Base):
    """Usuarios que responderán los cuestionarios"""
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    area_id = Column(Integer, ForeignKey("areas.id", ondelete="CASCADE"), nullable=False)
    email = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    position = Column(String(255), nullable=True)  # Cargo
    phone = Column(String(50), nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Índice único: email único por empresa (a través del área)
    __table_args__ = (
        UniqueConstraint('area_id', 'email', name='uq_user_area_email'),
    )
    
    # Relaciones
    area = relationship("Area", back_populates="users")
    assignments = relationship("QuestionAssignment", back_populates="user", cascade="all, delete-orphan")
    access_tokens = relationship("AccessToken", back_populates="user", cascade="all, delete-orphan")


class AdminUser(Base):
    """Usuarios administradores del sistema (Backoffice)"""
    __tablename__ = "admin_users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255), nullable=False)
    is_superadmin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    last_login = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)


# ============================================================================
# BANCO DE PREGUNTAS Y CUESTIONARIOS
# ============================================================================

class Category(Base):
    """Categorías para organizar preguntas (Ej: Ley Karin, ISO 27001, etc.)"""
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True)
    code = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    color = Column(String(7), default="#3B82F6")  # Hex color
    icon = Column(String(50), nullable=True)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    questions = relationship("Question", back_populates="category")


class Question(Base):
    """Banco de preguntas"""
    __tablename__ = "questions"
    
    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id", ondelete="SET NULL"), nullable=True)
    code = Column(String(50), nullable=True)  # Código único de la pregunta
    text = Column(Text, nullable=False)
    description = Column(Text, nullable=True)  # Ayuda o contexto
    question_type = Column(SQLEnum(QuestionType), nullable=False)
    options = Column(JSON, nullable=True)  # Para single/multiple choice: [{"value": "a", "text": "Opción A", "score": 10}]
    max_score = Column(Float, default=100.0)  # Puntaje máximo posible
    weight = Column(Float, default=1.0)  # Peso relativo de la pregunta
    required = Column(Boolean, default=True)
    order = Column(Integer, default=0)
    is_active = Column(Boolean, default=True)
    tags = Column(JSON, nullable=True)  # ["compliance", "technical", "governance"]
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    category = relationship("Category", back_populates="questions")
    assignments = relationship("QuestionAssignment", back_populates="question", cascade="all, delete-orphan")


# ============================================================================
# ASIGNACIONES Y CUESTIONARIOS
# ============================================================================

class QuestionnaireAssignment(Base):
    """Asignación de cuestionario a una empresa (campaña)"""
    __tablename__ = "questionnaire_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False)
    name = Column(String(255), nullable=False)  # Nombre de la campaña
    description = Column(Text, nullable=True)
    start_date = Column(DateTime, nullable=True)
    end_date = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)
    send_reminders = Column(Boolean, default=True)
    reminder_days = Column(Integer, default=3)  # Recordatorio cada X días
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    company = relationship("Company", back_populates="questionnaire_assignments")
    question_assignments = relationship("QuestionAssignment", back_populates="questionnaire", cascade="all, delete-orphan")
    divergence_alerts = relationship("DivergenceAlert", back_populates="questionnaire", cascade="all, delete-orphan")


class QuestionAssignment(Base):
    """Asignación de pregunta específica a usuario específico"""
    __tablename__ = "question_assignments"
    
    id = Column(Integer, primary_key=True, index=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaire_assignments.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    order = Column(Integer, default=0)
    is_mandatory = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índice único para evitar duplicados
    __table_args__ = (
        UniqueConstraint('questionnaire_id', 'question_id', 'user_id', name='uq_assignment'),
    )
    
    # Relaciones
    questionnaire = relationship("QuestionnaireAssignment", back_populates="question_assignments")
    question = relationship("Question", back_populates="assignments")
    user = relationship("User", back_populates="assignments")
    response = relationship("Response", back_populates="assignment", uselist=False, cascade="all, delete-orphan")


# ============================================================================
# TOKENS DE ACCESO Y RESPUESTAS
# ============================================================================

class AccessToken(Base):
    """Token único de acceso para cada usuario/cuestionario"""
    __tablename__ = "access_tokens"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    questionnaire_id = Column(Integer, ForeignKey("questionnaire_assignments.id", ondelete="CASCADE"), nullable=False)
    token = Column(String(64), unique=True, nullable=False, index=True)
    status = Column(SQLEnum(TokenStatus), default=TokenStatus.PENDING)
    sent_at = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    expires_at = Column(DateTime, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Índice único
    __table_args__ = (
        UniqueConstraint('user_id', 'questionnaire_id', name='uq_token_user_questionnaire'),
    )
    
    # Relaciones
    user = relationship("User", back_populates="access_tokens")


class Response(Base):
    """Respuestas de los usuarios"""
    __tablename__ = "responses"
    
    id = Column(Integer, primary_key=True, index=True)
    assignment_id = Column(Integer, ForeignKey("question_assignments.id", ondelete="CASCADE"), nullable=False, unique=True)
    answer = Column(JSON, nullable=False)  # Almacena la respuesta en formato flexible
    score = Column(Float, nullable=True)  # Puntaje calculado
    answered_at = Column(DateTime, default=datetime.utcnow)
    time_spent_seconds = Column(Integer, nullable=True)  # Tiempo en responder
    
    # Relaciones
    assignment = relationship("QuestionAssignment", back_populates="response")


# ============================================================================
# ALERTAS DE DIVERGENCIA (Core del negocio)
# ============================================================================

class DivergenceAlert(Base):
    """Alertas cuando hay respuestas contradictorias entre usuarios"""
    __tablename__ = "divergence_alerts"
    
    id = Column(Integer, primary_key=True, index=True)
    questionnaire_id = Column(Integer, ForeignKey("questionnaire_assignments.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(Integer, ForeignKey("questions.id", ondelete="CASCADE"), nullable=False)
    severity = Column(SQLEnum(AlertSeverity), default=AlertSeverity.MEDIUM)
    responses_data = Column(JSON, nullable=False)  # [{user_id, user_name, area, answer, score}]
    variance = Column(Float, nullable=True)  # Varianza entre respuestas
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relaciones
    questionnaire = relationship("QuestionnaireAssignment", back_populates="divergence_alerts")
    question = relationship("Question")


# ============================================================================
# CONFIGURACIÓN SMTP POR EMPRESA
# ============================================================================

class SMTPConfig(Base):
    """Configuración de correo por empresa"""
    __tablename__ = "smtp_configs"
    
    id = Column(Integer, primary_key=True, index=True)
    company_id = Column(Integer, ForeignKey("companies.id", ondelete="CASCADE"), nullable=False, unique=True)
    host = Column(String(255), nullable=False)
    port = Column(Integer, default=587)
    username = Column(String(255), nullable=False)
    password = Column(String(255), nullable=False)  # Encriptado
    use_tls = Column(Boolean, default=True)
    use_ssl = Column(Boolean, default=False)
    from_email = Column(String(255), nullable=False)
    from_name = Column(String(255), nullable=True)
    reply_to = Column(String(255), nullable=True)
    is_active = Column(Boolean, default=True)
    last_test_at = Column(DateTime, nullable=True)
    last_test_success = Column(Boolean, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relaciones
    company = relationship("Company", back_populates="smtp_config")


# ============================================================================
# CONFIGURACIÓN GLOBAL DEL SISTEMA
# ============================================================================

class SystemConfig(Base):
    """Configuración global del sistema"""
    __tablename__ = "system_config"
    
    id = Column(Integer, primary_key=True, index=True)
    key = Column(String(100), unique=True, nullable=False)
    value = Column(Text, nullable=True)
    description = Column(Text, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)


# ============================================================================
# LOGS DE AUDITORÍA
# ============================================================================

class AuditLog(Base):
    """Log de auditoría de acciones"""
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("admin_users.id"), nullable=True)
    action = Column(String(100), nullable=False)
    entity_type = Column(String(100), nullable=True)
    entity_id = Column(Integer, nullable=True)
    old_values = Column(JSON, nullable=True)
    new_values = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
