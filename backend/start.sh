#!/bin/bash
set -e

echo "🚀 Iniciando CyberGAP Backend..."
echo "📁 Directorio actual: $(pwd)"
echo "📋 Contenido de /app:"
ls -la /app/

echo ""
echo "🔍 Verificando imports de Python..."
python -c "
print('Importando módulos...')
try:
    print('  - fastapi...')
    from fastapi import FastAPI
    print('  - sqlalchemy...')
    from sqlalchemy import create_engine
    print('  - pydantic...')
    from pydantic import BaseModel
    print('  - jose...')
    from jose import jwt
    print('  - passlib...')
    from passlib.context import CryptContext
    print('  - cryptography...')
    from cryptography.fernet import Fernet
    print('✅ Todos los módulos externos OK')
except Exception as e:
    print(f'❌ Error en módulos externos: {e}')
    exit(1)

print('')
print('Importando aplicación...')
try:
    print('  - models...')
    from app.models import Base, AdminUser
    print('  - database...')
    from app.database import engine, init_db
    print('  - schemas...')
    from app import schemas
    print('  - security...')
    from app.utils.security import hash_password, create_access_token
    print('  - routers...')
    from app.routers import auth_router, companies_router
    print('  - main...')
    from app.main import app
    print('✅ Aplicación importada correctamente')
except Exception as e:
    print(f'❌ Error importando aplicación: {e}')
    import traceback
    traceback.print_exc()
    exit(1)
"

echo ""
echo "✅ Verificación completa. Iniciando servidor..."
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
