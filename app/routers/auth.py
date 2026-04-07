from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Role, UserRole
from app.schemas import UserCreate, UserResponse, LoginRequest, TokenResponse
from app.auth import verify_password, get_password_hash, create_access_token, get_current_user_required

router = APIRouter(tags=["Authentication"])

@router.post("/api/register/", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    if user_data.password != user_data.confirm_password:
        raise HTTPException(400, "Passwords do not match")
    
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(400, "Email already registered")
    
    new_user = User(
        first_name=user_data.first_name,
        last_name=user_data.last_name,
        patronomic_name=user_data.patronomic_name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        is_active=True
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    
    # Назначаем роль "user"
    user_role = db.query(Role).filter(Role.name == "user").first()
    if user_role:
        db.add(UserRole(user_id=new_user.id, role_id=user_role.id))
        db.commit()
    
    return new_user

@router.post("/api/login/", response_model=TokenResponse)
def login(login_data: LoginRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email, User.is_active == True).first()
    
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid credentials")
    
    token = create_access_token({"user_id": user.id, "sub": user.email}, user.token_version)
    
    return TokenResponse(access_token=token, token_type="bearer", user_id=user.id, email=user.email)

@router.post("/api/logout/")
def logout(current_user = Depends(get_current_user_required), db: Session = Depends(get_db)):
    current_user.token_version += 1
    db.commit()
    return {"message": "Logged out"}