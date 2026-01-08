"""
Utilidades de Seguridad - JWT, Hashing, Tokens
"""
import os
import secrets
import hashlib
import base64
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet

# Configuración
SECRET_KEY = os.getenv("SECRET_KEY", secrets.token_urlsafe(32))
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))  # 8 horas

# Encriptación para contraseñas SMTP
def get_fernet_key():
    """Obtener clave Fernet válida desde variable de entorno o generar una"""
    env_key = os.getenv("ENCRYPTION_KEY")
    if env_key:
        # Si la clave tiene 32 bytes, convertirla a formato Fernet (base64)
        if len(env_key) == 32:
            return base64.urlsafe_b64encode(env_key.encode()).decode()
        # Si ya parece ser base64, usarla directamente
        try:
            # Verificar que es una clave Fernet válida
            Fernet(env_key.encode() if isinstance(env_key, str) else env_key)
            return env_key
        except Exception:
            # Si no es válida, generar una derivada
            return base64.urlsafe_b64encode(hashlib.sha256(env_key.encode()).digest()).decode()
    # Generar clave por defecto
    return Fernet.generate_key().decode()

ENCRYPTION_KEY = get_fernet_key()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
fernet = Fernet(ENCRYPTION_KEY.encode() if isinstance(ENCRYPTION_KEY, str) else ENCRYPTION_KEY)


def get_password_hash(password: str) -> str:
    """Generar hash de contraseña (trunca a 72 bytes para bcrypt)"""
    # bcrypt tiene límite de 72 bytes
    password = password[:72] if len(password.encode('utf-8')) > 72 else password
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña contra hash"""
    # Truncar igual que al hashear
    plain_password = plain_password[:72] if len(plain_password.encode('utf-8')) > 72 else plain_password
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Crear token JWT"""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def decode_token(token: str) -> Optional[dict]:
    """Decodificar token JWT"""
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None


def generate_unique_token(length: int = 32) -> str:
    """Generar token único para acceso a cuestionarios"""
    return secrets.token_urlsafe(length)


def encrypt_password(password: str) -> str:
    """Encriptar contraseña SMTP"""
    return fernet.encrypt(password.encode()).decode()


def decrypt_password(encrypted_password: str) -> str:
    """Desencriptar contraseña SMTP"""
    return fernet.decrypt(encrypted_password.encode()).decode()


def hash_token(token: str) -> str:
    """Hash de token para búsqueda segura (no reversible)"""
    return hashlib.sha256(token.encode()).hexdigest()


# Alias para compatibilidad
hash_password = get_password_hash
