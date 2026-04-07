from pydantic import BaseModel, EmailStr
from typing import Optional

# User
class UserCreate(BaseModel):
    first_name: str
    last_name: str
    patronomic_name: Optional[str] = None
    email: EmailStr
    password: str
    confirm_password: str

class UserUpdate(BaseModel):
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    patronomic_name: Optional[str] = None

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    patronomic_name: Optional[str]
    is_active: bool

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    user_id: int
    email: str

# Admin
class RoleCreate(BaseModel):
    name: str

class RoleResponse(BaseModel):
    id: int
    name: str

class ElementCreate(BaseModel):
    name: str

class ElementResponse(BaseModel):
    id: int
    name: str

class AccessRuleCreate(BaseModel):
    role_name: str
    element_name: str
    can_read_own: bool = False
    can_read_all: bool = False
    can_create: bool = False
    can_update_own: bool = False
    can_update_all: bool = False
    can_delete_own: bool = False
    can_delete_all: bool = False

class AssignRoleRequest(BaseModel):
    user_email: str
    role_name: str