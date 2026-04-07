from sqlalchemy.orm import Session
from app.models import User, UserRole, AccessRule, BusinessElement

def check_permission(db: Session, user: User, element_name: str, action: str, obj=None) -> bool:
    """
    Проверка прав доступа
    action: 'read', 'create', 'update', 'delete'
    obj: объект с атрибутом owner_id (для проверки своих/чужих)
    """
    if not user or not user.is_active:
        return False
    
    # Суперпользователь может всё
    if user.is_superuser:
        return True
    
    # Получаем роли пользователя
    user_roles = db.query(UserRole).filter(UserRole.user_id == user.id).all()
    if not user_roles:
        return False
    
    role_ids = [ur.role_id for ur in user_roles]
    
    # Получаем бизнес-элемент
    element = db.query(BusinessElement).filter(BusinessElement.name == element_name).first()
    if not element:
        return False
    
    # Определяем, какое право проверять
    if action == "create":
        field = "can_create"
    elif action == "read":
        field = "can_read_own" if (obj and getattr(obj, "owner_id", None) == user.id) else "can_read_all"
    elif action == "update":
        field = "can_update_own" if (obj and getattr(obj, "owner_id", None) == user.id) else "can_update_all"
    elif action == "delete":
        field = "can_delete_own" if (obj and getattr(obj, "owner_id", None) == user.id) else "can_delete_all"
    else:
        return False
    
    # Проверяем правила для всех ролей
    rules = db.query(AccessRule).filter(
        AccessRule.role_id.in_(role_ids),
        AccessRule.element_id == element.id
    ).all()
    
    return any(getattr(rule, field, False) for rule in rules)