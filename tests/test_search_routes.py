from models import Document, Deputy, FAQ, News


def test_search_returns_matches_for_all_sections(client, session):
    news = News(title="Transparency report", body="City transparency plan")
    document = Document(
        title="Transparency roadmap",
        summary="Detailed roadmap",
        doc_type="policy",
    )
    deputy = Deputy(full_name="Ivan Transparency", bio="Advocates transparency")
    faq = FAQ(question="What is transparency?", answer="It is openness")

    session.add_all([news, document, deputy, faq])
    session.commit()

    response = client.get("/search/?q=transparency")
    text = response.get_data(as_text=True)

    assert "Transparency report" in text
    assert "Transparency roadmap" in text
    assert "Ivan Transparency" in text
    assert "What is transparency?" in text


def test_search_without_query_shows_prompt(client):
    response = client.get("/search/")
    text = response.get_data(as_text=True)

    assert "Введите запрос" in text
    assert "Ничего не найдено" not in text
