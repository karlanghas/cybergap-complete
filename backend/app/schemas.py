"""
Schemas Pydantic para validación y serialización
"""
from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, EmailStr, Field, ConfigDict
from enum import Enum


# ============================================================================
# ENUMS
# ============================================================================

class QuestionTypeEnum(str, Enum):
    SINGLE_CHOICE = "single_choice"
    MULTIPLE_CHOICE = "multiple_choice"
    TEXT = "text"
    SCALE = "scale"
    YES_NO = "yes_no"


class TokenStatusEnum(str, Enum):
    PENDING = "pending"
    SENT = "sent"
    OPENED = "opened"
    COMPLETED = "completed"
    EXPIRED = "expired"


class AlertSeverityEnum(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


# ============================================================================
# BASE SCHEMAS
# ============================================================================

class BaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)


# ============================================================================
# COMPANY SCHEMAS
# ============================================================================

class CompanyBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    rut: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None


class CompanyCreate(CompanyBase):
    pass


class CompanyUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    rut: Optional[str] = None
    industry: Optional[str] = None
    logo_url: Optional[str] = None
    is_active: Optional[bool] = None


class CompanyResponse(CompanyBase, BaseSchema):
    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class CompanyWithStats(CompanyResponse):
    areas_count: int = 0
    users_count: int = 0
    questionnaires_count: int = 0
    completion_rate: float = 0.0


# ============================================================================
# AREA SCHEMAS
# ============================================================================

class AreaBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: Optional[str] = None
    description: Optional[str] = None
    order: int = 0


class AreaCreate(AreaBase):
    company_id: int
    parent_id: Optional[int] = None


class AreaUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = None
    description: Optional[str] = None
    parent_id: Optional[int] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class AreaResponse(AreaBase, BaseSchema):
    id: int
    company_id: int
    parent_id: Optional[int]
    is_active: bool
    created_at: datetime


class AreaWithChildren(AreaResponse):
    children: List["AreaWithChildren"] = []
    users_count: int = 0


# ============================================================================
# USER SCHEMAS
# ============================================================================

class UserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)
    position: Optional[str] = None
    phone: Optional[str] = None


class UserCreate(UserBase):
    area_id: int


class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = Field(None, min_length=2, max_length=255)
    position: Optional[str] = None
    phone: Optional[str] = None
    area_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponse(UserBase, BaseSchema):
    id: int
    area_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserWithArea(UserResponse):
    area_name: str = ""
    company_id: int = 0
    company_name: str = ""


# ============================================================================
# ADMIN USER SCHEMAS
# ============================================================================

class AdminUserBase(BaseModel):
    email: EmailStr
    full_name: str = Field(..., min_length=2, max_length=255)


class AdminUserCreate(AdminUserBase):
    password: str = Field(..., min_length=8)
    is_superadmin: bool = False


class AdminUserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = Field(None, min_length=8)
    is_superadmin: Optional[bool] = None
    is_active: Optional[bool] = None


class AdminUserResponse(AdminUserBase, BaseSchema):
    id: int
    is_superadmin: bool
    is_active: bool
    last_login: Optional[datetime]
    created_at: datetime


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# ============================================================================
# CATEGORY SCHEMAS
# ============================================================================

class CategoryBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    code: Optional[str] = None
    description: Optional[str] = None
    color: str = "#3B82F6"
    icon: Optional[str] = None
    order: int = 0


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    code: Optional[str] = None
    description: Optional[str] = None
    color: Optional[str] = None
    icon: Optional[str] = None
    order: Optional[int] = None
    is_active: Optional[bool] = None


class CategoryResponse(CategoryBase, BaseSchema):
    id: int
    is_active: bool
    created_at: datetime


class CategoryWithCount(CategoryResponse):
    questions_count: int = 0


# ============================================================================
# QUESTION SCHEMAS
# ============================================================================

class QuestionOption(BaseModel):
    value: str
    text: str
    score: float = 0


class QuestionBase(BaseModel):
    code: Optional[str] = None
    text: str = Field(..., min_length=5)
    description: Optional[str] = None
    question_type: QuestionTypeEnum
    options: Optional[List[QuestionOption]] = None
    max_score: float = 100.0
    weight: float = 1.0
    required: bool = True
    order: int = 0
    tags: Optional[List[str]] = None


class QuestionCreate(QuestionBase):
    category_id: Optional[int] = None


class QuestionUpdate(BaseModel):
    category_id: Optional[int] = None
    code: Optional[str] = None
    text: Optional[str] = None
    description: Optional[str] = None
    question_type: Optional[QuestionTypeEnum] = None
    options: Optional[List[QuestionOption]] = None
    max_score: Optional[float] = None
    weight: Optional[float] = None
    required: Optional[bool] = None
    order: Optional[int] = None
    tags: Optional[List[str]] = None
    is_active: Optional[bool] = None


class QuestionResponse(QuestionBase, BaseSchema):
    id: int
    category_id: Optional[int]
    is_active: bool
    created_at: datetime
    updated_at: datetime


class QuestionWithCategory(QuestionResponse):
    category_name: Optional[str] = None
    category_color: Optional[str] = None


# ============================================================================
# QUESTIONNAIRE ASSIGNMENT SCHEMAS
# ============================================================================

class QuestionnaireAssignmentBase(BaseModel):
    name: str = Field(..., min_length=2, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    send_reminders: bool = True
    reminder_days: int = 3


class QuestionnaireAssignmentCreate(QuestionnaireAssignmentBase):
    company_id: int


class QuestionnaireAssignmentUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=2, max_length=255)
    description: Optional[str] = None
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    send_reminders: Optional[bool] = None
    reminder_days: Optional[int] = None


class QuestionnaireAssignmentResponse(QuestionnaireAssignmentBase, BaseSchema):
    id: int
    company_id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class QuestionnaireWithStats(QuestionnaireAssignmentResponse):
    company_name: str = ""
    total_assignments: int = 0
    completed_assignments: int = 0
    completion_rate: float = 0.0
    divergence_alerts_count: int = 0


# ============================================================================
# QUESTION ASSIGNMENT SCHEMAS
# ============================================================================

class QuestionAssignmentBase(BaseModel):
    order: int = 0
    is_mandatory: bool = True


class QuestionAssignmentCreate(QuestionAssignmentBase):
    questionnaire_id: int
    question_id: int
    user_id: int


class QuestionAssignmentBulkCreate(BaseModel):
    questionnaire_id: int
    assignments: List[Dict[str, int]]  # [{question_id: x, user_id: y}]


class QuestionAssignmentResponse(QuestionAssignmentBase, BaseSchema):
    id: int
    questionnaire_id: int
    question_id: int
    user_id: int
    created_at: datetime


class QuestionAssignmentWithDetails(QuestionAssignmentResponse):
    question_text: str = ""
    question_type: QuestionTypeEnum
    user_name: str = ""
    user_email: str = ""
    area_name: str = ""
    is_answered: bool = False


# ============================================================================
# ACCESS TOKEN SCHEMAS
# ============================================================================

class AccessTokenResponse(BaseSchema):
    id: int
    user_id: int
    questionnaire_id: int
    token: str
    status: TokenStatusEnum
    sent_at: Optional[datetime]
    opened_at: Optional[datetime]
    completed_at: Optional[datetime]
    expires_at: Optional[datetime]
    created_at: datetime


class SendTokensRequest(BaseModel):
    questionnaire_id: int
    user_ids: Optional[List[int]] = None  # None = todos los usuarios asignados


# ============================================================================
# RESPONSE SCHEMAS
# ============================================================================

class ResponseBase(BaseModel):
    answer: Any  # Puede ser string, lista, número dependiendo del tipo


class ResponseCreate(ResponseBase):
    assignment_id: int
    time_spent_seconds: Optional[int] = None


class ResponseSubmit(BaseModel):
    """Para envío desde el formulario público"""
    token: str
    responses: List[Dict[str, Any]]  # [{assignment_id: x, answer: y, time_spent: z}]


class ResponseResponse(ResponseBase, BaseSchema):
    id: int
    assignment_id: int
    score: Optional[float]
    answered_at: datetime
    time_spent_seconds: Optional[int]


# ============================================================================
# DIVERGENCE ALERT SCHEMAS
# ============================================================================

class DivergenceAlertResponse(BaseSchema):
    id: int
    questionnaire_id: int
    question_id: int
    severity: AlertSeverityEnum
    responses_data: List[Dict[str, Any]]
    variance: Optional[float]
    is_resolved: bool
    resolved_at: Optional[datetime]
    resolution_notes: Optional[str]
    created_at: datetime


class DivergenceAlertWithDetails(DivergenceAlertResponse):
    question_text: str = ""
    questionnaire_name: str = ""
    company_name: str = ""


class ResolveAlertRequest(BaseModel):
    resolution_notes: str


# ============================================================================
# SMTP CONFIG SCHEMAS
# ============================================================================

class SMTPConfigBase(BaseModel):
    host: str
    port: int = 587
    username: str
    use_tls: bool = True
    use_ssl: bool = False
    from_email: EmailStr
    from_name: Optional[str] = None
    reply_to: Optional[EmailStr] = None


class SMTPConfigCreate(SMTPConfigBase):
    company_id: int
    password: str


class SMTPConfigUpdate(BaseModel):
    host: Optional[str] = None
    port: Optional[int] = None
    username: Optional[str] = None
    password: Optional[str] = None
    use_tls: Optional[bool] = None
    use_ssl: Optional[bool] = None
    from_email: Optional[EmailStr] = None
    from_name: Optional[str] = None
    reply_to: Optional[EmailStr] = None
    is_active: Optional[bool] = None


class SMTPConfigResponse(SMTPConfigBase, BaseSchema):
    id: int
    company_id: int
    is_active: bool
    last_test_at: Optional[datetime]
    last_test_success: Optional[bool]
    created_at: datetime


class SMTPTestRequest(BaseModel):
    test_email: EmailStr


# ============================================================================
# REPORT SCHEMAS
# ============================================================================

class ComplianceScore(BaseModel):
    area_id: int
    area_name: str
    score: float
    max_score: float
    percentage: float
    questions_answered: int
    total_questions: int


class CompanyReport(BaseModel):
    company_id: int
    company_name: str
    overall_score: float
    overall_percentage: float
    areas_scores: List[ComplianceScore]
    categories_scores: List[Dict[str, Any]]
    divergence_alerts: List[DivergenceAlertWithDetails]


class DashboardStats(BaseModel):
    total_companies: int
    total_users: int
    total_questions: int
    active_questionnaires: int
    pending_responses: int
    completed_responses: int
    divergence_alerts: int
    completion_rate: float


# ============================================================================
# PUBLIC QUESTIONNAIRE SCHEMAS (Para formulario público)
# ============================================================================

class PublicQuestionnaireInfo(BaseModel):
    questionnaire_name: str
    company_name: str
    company_logo: Optional[str]
    user_name: str
    total_questions: int
    deadline: Optional[datetime]


class PublicQuestion(BaseModel):
    assignment_id: int
    question_id: int
    text: str
    description: Optional[str]
    question_type: QuestionTypeEnum
    options: Optional[List[QuestionOption]]
    required: bool
    order: int


class PublicQuestionnaire(BaseModel):
    info: PublicQuestionnaireInfo
    questions: List[PublicQuestion]


# Resolver forward references
AreaWithChildren.model_rebuild()
