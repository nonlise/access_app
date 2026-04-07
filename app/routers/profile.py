from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.schemas import UserResponse, UserUpdate
from app.auth import get_current_user_required

router = APIRouter(tags=["Profile"])

@router.get("/api/profile/", response_model=UserResponse)
def get_profile(current_user: User = Depends(get_current_user_required)):
    return current_user

@router.put("/api/profile/", response_model=UserResponse)
def update_profile(
    user_data: UserUpdate,
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    if user_data.first_name:
        current_user.first_name = user_data.first_name
    if user_data.last_name:
        current_user.last_name = user_data.last_name
    if user_data.patronomic_name is not None:
        current_user.patronomic_name = user_data.patronomic_name
    
    db.commit()
    db.refresh(current_user)
    return current_user

@router.post("/api/profile/delete/")
def delete_account(
    current_user: User = Depends(get_current_user_required),
    db: Session = Depends(get_db)
):
    current_user.is_active = False
    current_user.token_version += 1
    db.commit()
    return {"message": "Account deactivated"}