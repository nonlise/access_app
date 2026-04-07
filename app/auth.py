from datetime import datetime, timedelta ,timezone
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends, Request
from sqlalchemy.orm import Session

from app.config import settings
from app.database import get_db
from app.models import User

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, token_version: int = 0):
    to_encode = data.copy()
    to_encode["token_version"] = token_version
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES) #datetime.utcnow()
    to_encode["exp"] = expire
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)

def decode_token(token: str):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
    except JWTError:
        return None

def get_current_user(request: Request, db: Session = Depends(get_db)):
    """Получить текущего пользователя из токена (или None)"""
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    payload = decode_token(token)
    if not payload:
        return None
    
    user_id = payload.get("user_id")
    token_version = payload.get("token_version")
    
    user = db.query(User).filter(User.id == user_id, User.is_active == True).first()
    if not user or user.token_version != token_version:
        return None
    
    return user

def get_current_user_required(current_user = Depends(get_current_user)):
    """Требует авторизации"""
    if not current_user:
        raise HTTPException(status_code=401, detail="Not authenticated")
    return current_user