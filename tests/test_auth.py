import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.database import Base, engine, get_db
from app.models import Role


client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_db():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    
    db = next(get_db())
    role = Role(name="user")
    db.add(role)
    db.commit()
    
    yield
    
    Base.metadata.drop_all(bind=engine)

def test_register_success():
    """Тест успешной регистрации"""
    response = client.post("/api/register/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "123456",
        "confirm_password": "123456"
    })
    assert response.status_code == 200
    assert response.json()["email"] == "test@example.com"

def test_register_password_mismatch():
    """Тест: пароли не совпадают"""
    response = client.post("/api/register/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": "test@example.com",
        "password": "123456",
        "confirm_password": "654321"
    })
    assert response.status_code == 400
    assert "Passwords do not match" in response.json()["detail"]

def test_login_success():
    """Тест успешного входа"""
    client.post("/api/register/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": "login@example.com",
        "password": "123456",
        "confirm_password": "123456"
    })
    
    response = client.post("/api/login/", json={
        "email": "login@example.com",
        "password": "123456"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_invalid_password():
    """Тест: неверный пароль"""
    client.post("/api/register/", json={
        "first_name": "Test",
        "last_name": "User",
        "email": "wrong@example.com",
        "password": "123456",
        "confirm_password": "123456"
    })
    
    response = client.post("/api/login/", json={
        "email": "wrong@example.com",
        "password": "wrongpassword"
    })
    assert response.status_code == 401

def test_protected_endpoint_without_token():
    """Тест: защищённый эндпоинт без токена"""
    response = client.get("/api/profile/")
    assert response.status_code == 401