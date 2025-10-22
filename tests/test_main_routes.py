from datetime import datetime, timedelta

from models import Event, News


def test_index_page_shows_recent_published_content(client, session):
    now = datetime.utcnow()
    for i in range(7):
        session.add(
            News(
                title=f"News {i}",
                body="Body",
                is_published=True,
                published_at=now - timedelta(days=i),
            )
        )
    session.add(
        News(
            title="Draft News",
            body="Draft Body",
            is_published=False,
            published_at=now,
        )
    )

    for i in range(6):
        session.add(
            Event(
                title=f"Event {i}",
                description="Desc",
                is_public=True,
                start_time=now + timedelta(days=i),
            )
        )
    session.add(
        Event(
            title="Private Event",
            description="Hidden",
            is_public=False,
            start_time=now,
        )
    )

    session.commit()

    response = client.get("/")
    assert response.status_code == 200

    text = response.get_data(as_text=True)
    # Only the five most recent published news items should be visible
    assert "News 0" in text
    assert "News 4" in text
    assert "News 5" not in text
    assert "News 6" not in text
    assert "Draft News" not in text

    # Only public events should be rendered
    assert "Event 0" in text
    assert "Event 4" in text
    assert "Event 5" not in text
    assert "Private Event" not in text
