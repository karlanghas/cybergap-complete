"""
Routers de la API
"""
from .auth import router as auth_router
from .companies import router as companies_router
from .areas import router as areas_router
from .users import router as users_router
from .questions import router as questions_router, category_router
from .questionnaires import router as questionnaires_router
from .public import router as public_router

__all__ = [
    "auth_router",
    "companies_router", 
    "areas_router",
    "users_router",
    "questions_router",
    "category_router",
    "questionnaires_router",
    "public_router"
]
