from datetime import datetime

from models import News


def _create_news(session, **kwargs):
    news = News(
        title=kwargs.get("title", "Sample News"),
        body=kwargs.get("body", "Sample body"),
        is_published=kwargs.get("is_published", True),
        published_at=kwargs.get("published_at", datetime.utcnow()),
    )
    session.add(news)
    session.commit()
    return news


def test_published_news_detail_renders(client, session):
    item = _create_news(session, title="Published")

    response = client.get(f"/news/{item.id}")
    assert response.status_code == 200
    assert "Published" in response.get_data(as_text=True)


def test_unpublished_news_returns_404(client, session):
    item = _create_news(session, title="Secret", is_published=False)

    response = client.get(f"/news/{item.id}")
    assert response.status_code == 404


def test_missing_news_returns_404(client):
    response = client.get("/news/999")
    assert response.status_code == 404
