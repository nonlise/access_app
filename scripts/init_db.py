import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.database import SessionLocal, engine, Base
from app.models import User, Role, UserRole, BusinessElement, AccessRule
from app.auth import get_password_hash

def init_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    # Роли
    roles = ["admin", "manager", "user", "guest"]
    role_objs = {}
    for name in roles:
        role = Role(name=name)
        db.add(role)
        role_objs[name] = role
    db.commit()
    
    # Бизнес-элементы
    elements = ["articles", "users", "roles", "rules"]
    element_objs = {}
    for name in elements:
        elem = BusinessElement(name=name)
        db.add(elem)
        element_objs[name] = elem
    db.commit()
    
    # Пользователи
    users = [
        {"first_name": "Admin", "last_name": "User", "email": "admin@example.com", "password": "admin123", "is_superuser": True},
        {"first_name": "John", "last_name": "Doe", "email": "john@example.com", "password": "user123"},
        {"first_name": "Jane", "last_name": "Smith", "email": "jane@example.com", "password": "user123"},
    ]
    
    user_objs = {}
    for u in users:
        user = User(
            first_name=u["first_name"],
            last_name=u["last_name"],
            email=u["email"],
            hashed_password=get_password_hash(u["password"]),
            is_superuser=u.get("is_superuser", False),
            is_active=True
        )
        db.add(user)
        user_objs[u["email"]] = user
    db.commit()
    
    # Назначение ролей
    db.add(UserRole(user_id=user_objs["admin@example.com"].id, role_id=role_objs["admin"].id))
    db.add(UserRole(user_id=user_objs["john@example.com"].id, role_id=role_objs["user"].id))
    db.add(UserRole(user_id=user_objs["jane@example.com"].id, role_id=role_objs["user"].id))
    
    # Правила доступа для articles
    # Админ может всё
    db.add(AccessRule(
        role_id=role_objs["admin"].id,
        element_id=element_objs["articles"].id,
        can_read_own=True, can_read_all=True,
        can_create=True,
        can_update_own=True, can_update_all=True,
        can_delete_own=True, can_delete_all=True
    ))
    
    # Пользователь: читает все, создаёт свои, редактирует/удаляет только свои
    db.add(AccessRule(
        role_id=role_objs["user"].id,
        element_id=element_objs["articles"].id,
        can_read_own=True, can_read_all=True,
        can_create=True,
        can_update_own=True, can_update_all=False,
        can_delete_own=True, can_delete_all=False
    ))
    
    db.commit()
    
    print("База данных инициализирована!")
    print("\nТестовые пользователи:")
    print("   admin@example.com / admin123 (суперпользователь)")
    print("   john@example.com / user123")
    print("   jane@example.com / user123")

if __name__ == "__main__":
    init_db()