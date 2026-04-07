from fastapi import FastAPI
from app.database import Base, engine
from app.routers import auth, profile, articles, admin

# Создаём таблицы
Base.metadata.create_all(bind=engine)

app = FastAPI(title="Auth System", description="Система аутентификации и авторизации")

# Подключаем роутеры
app.include_router(auth.router)
app.include_router(profile.router)
app.include_router(articles.router)
app.include_router(admin.router)

@app.get("/")
def root():
    return {"message": "Auth System API", "docs": "/docs"}