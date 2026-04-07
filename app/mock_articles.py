class MockArticle:
    def __init__(self, id: int, title: str, owner_id: int):
        self.id = id
        self.title = title
        self.owner_id = owner_id

# Хранилище в памяти
articles_store = {
    1: MockArticle(1, "Моя первая статья", owner_id=1),
    2: MockArticle(2, "Новости дня", owner_id=2),
}

def get_article(article_id: int):
    return articles_store.get(article_id)