from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import User
from app.auth import get_current_user_required
from app.permissions import check_permission
from app.mock_articles import articles_store, MockArticle

router = APIRouter(tags=["Articles"])

@router.get("/api/articles/")
def list_articles(current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)):
    if not check_permission(db, current_user, "articles", "read"):
        raise HTTPException(403, "Forbidden")
    
    return {"articles": [{"id": a.id, "title": a.title, "owner_id": a.owner_id} for a in articles_store.values()]}

@router.post("/api/articles/create/")
def create_article(title: str, current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)):
    if not check_permission(db, current_user, "articles", "create"):
        raise HTTPException(403, "Forbidden: no create permission")
    
    new_id = max(articles_store.keys()) + 1 if articles_store else 1
    articles_store[new_id] = MockArticle(new_id, title, current_user.id)
    
    return {"message": "Article created", "article": {"id": new_id, "title": title}}

@router.delete("/api/articles/{article_id}/delete/")
def delete_article(article_id: int, current_user: User = Depends(get_current_user_required), db: Session = Depends(get_db)):
    if article_id not in articles_store:
        raise HTTPException(404, "Article not found")
    
    article = articles_store[article_id]
    
    if not check_permission(db, current_user, "articles", "delete", obj=article):
        raise HTTPException(403, "Forbidden: no delete permission")
    
    del articles_store[article_id]
    return {"message": "Article deleted"}