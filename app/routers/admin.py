from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User, Role, UserRole, BusinessElement, AccessRule
from app.schemas import RoleCreate, RoleResponse, ElementCreate, ElementResponse, AccessRuleCreate, AssignRoleRequest
from app.auth import get_current_user_required

router = APIRouter(prefix="/api/admin", tags=["Admin"])

def require_admin(current_user = Depends(get_current_user_required), db: Session = Depends(get_db)):
    """Проверка прав администратора"""
    if current_user.is_superuser:
        return current_user
    
    user_roles = db.query(UserRole).join(Role).filter(
        UserRole.user_id == current_user.id,
        Role.name == "admin"
    ).first()
    
    if not user_roles:
        raise HTTPException(403, "Admin access required")
    return current_user

# Роли
@router.get("/roles/", response_model=list[RoleResponse])
def list_roles(_ = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(Role).all()

@router.post("/roles/", response_model=RoleResponse)
def create_role(role_data: RoleCreate, _ = Depends(require_admin), db: Session = Depends(get_db)):
    if db.query(Role).filter(Role.name == role_data.name).first():
        raise HTTPException(400, "Role already exists")
    
    new_role = Role(name=role_data.name)
    db.add(new_role)
    db.commit()
    db.refresh(new_role)
    return new_role

# Business элементы
@router.get("/elements/", response_model=list[ElementResponse])
def list_elements(_ = Depends(require_admin), db: Session = Depends(get_db)):
    return db.query(BusinessElement).all()

@router.post("/elements/", response_model=ElementResponse)
def create_element(element_data: ElementCreate, _ = Depends(require_admin), db: Session = Depends(get_db)):
    if db.query(BusinessElement).filter(BusinessElement.name == element_data.name).first():
        raise HTTPException(400, "Element already exists")
    
    new_element = BusinessElement(name=element_data.name)
    db.add(new_element)
    db.commit()
    db.refresh(new_element)
    return new_element

@router.delete("/elements/{element_id}/")
def delete_element(
    element_id: int, 
    _ = Depends(require_admin), 
    db: Session = Depends(get_db)
):
    element = db.query(BusinessElement).filter(BusinessElement.id == element_id).first()
    if not element:
        raise HTTPException(404, "Business element not found")
    
    rules_with_element = db.query(AccessRule).filter(AccessRule.element_id == element_id).first()
    if rules_with_element:
        raise HTTPException(400, "Cannot delete element: access rules are using this element")
    
    db.query(AccessRule).filter(AccessRule.element_id == element_id).delete()
    
    db.delete(element)
    db.commit()
    
    return {"message": f"Business element '{element.name}' deleted successfully"}

# Access Rules
@router.get("/rules/")
def list_rules(_ = Depends(require_admin), db: Session = Depends(get_db)):
    rules = db.query(AccessRule).all()
    result = []
    for rule in rules:
        role = db.query(Role).get(rule.role_id)
        element = db.query(BusinessElement).get(rule.element_id)
        result.append({
            "id": rule.id,
            "role": role.name if role else None,
            "element": element.name if element else None,
            "can_read_own": rule.can_read_own,
            "can_read_all": rule.can_read_all,
            "can_create": rule.can_create,
            "can_update_own": rule.can_update_own,
            "can_update_all": rule.can_update_all,
            "can_delete_own": rule.can_delete_own,
            "can_delete_all": rule.can_delete_all,
        })
    return result

@router.post("/rules/")
def create_rule(rule_data: AccessRuleCreate, _ = Depends(require_admin), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.name == rule_data.role_name).first()
    if not role:
        raise HTTPException(404, "Role not found")
    
    element = db.query(BusinessElement).filter(BusinessElement.name == rule_data.element_name).first()
    if not element:
        raise HTTPException(404, "Element not found")
    
    existing = db.query(AccessRule).filter(
        AccessRule.role_id == role.id,
        AccessRule.element_id == element.id
    ).first()
    
    if existing:
        for key, value in rule_data.dict(exclude={"role_name", "element_name"}).items():
            setattr(existing, key, value)
        db.commit()
        return {"message": "Rule updated", "id": existing.id}
    
    new_rule = AccessRule(role_id=role.id, element_id=element.id, **rule_data.dict(exclude={"role_name", "element_name"}))
    db.add(new_rule)
    db.commit()
    db.refresh(new_rule)
    return {"message": "Rule created", "id": new_rule.id}

@router.post("/assign-role/")
def assign_role(assign_data: AssignRoleRequest, _ = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == assign_data.user_email).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    role = db.query(Role).filter(Role.name == assign_data.role_name).first()
    if not role:
        raise HTTPException(404, "Role not found")
    
    existing = db.query(UserRole).filter(
        UserRole.user_id == user.id,
        UserRole.role_id == role.id
    ).first()
    
    if existing:
        raise HTTPException(400, "Role already assigned")
    
    db.add(UserRole(user_id=user.id, role_id=role.id))
    db.commit()
    return {"message": f"Role '{role.name}' assigned to {user.email}"}

@router.delete("/roles/{role_id}/")
def delete_role(role_id: int, _ = Depends(require_admin), db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(404, "Role not found")
    
    users_with_role = db.query(UserRole).filter(UserRole.role_id == role_id).first()
    if users_with_role:
        raise HTTPException(400, "Cannot delete role: users are assigned to this role")
    
    db.query(AccessRule).filter(AccessRule.role_id == role_id).delete()
    
    db.delete(role) 
    db.commit()
    return {"message": f"Role '{role.name}' deleted successfully"}