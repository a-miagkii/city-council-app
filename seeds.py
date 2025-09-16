from datetime import datetime, timedelta
from extensions import db
from models import User, News, Document, Event, Deputy, FAQ
from app import create_app

app = create_app()

with app.app_context():
    db.drop_all()
    db.create_all()

    admin = User(email="admin@example.com", name="Администратор", role="admin")
    admin.set_password("admin123")
    user = User(email="user@example.com", name="Иван Пользователь", role="user")
    user.set_password("user123")

    db.session.add_all([admin, user])

    # News
    for i in range(1, 6):
        n = News(
            title=f"Решение №{100+i} принято",
            body="Краткое описание решения и его последствий для жителей. " * 3,
            published_at=datetime.utcnow() - timedelta(days=i),
            created_by=admin,
            is_published=True
        )
        db.session.add(n)

    # Documents
    docs = [
        Document(title="Постановление о бюджете", summary="Утверждение бюджета на 2025 год.", doc_type="постановление", file_url="#"),
        Document(title="Проект закона о транспорте", summary="Проект по развитию общественного транспорта.", doc_type="проект", file_url="#"),
        Document(title="Решение о благоустройстве", summary="Программа благоустройства дворов.", doc_type="решение", file_url="#"),
    ]
    db.session.add_all(docs)

    # Events
    for i in range(3):
        e = Event(
            title=f"Заседание комиссии #{i+1}",
            description="Обсуждение повестки и вопросов жителей.",
            start_time=datetime.utcnow() + timedelta(days=i+1),
            end_time=datetime.utcnow() + timedelta(days=i+1, hours=2),
            location="Зал заседаний №1",
            is_public=True
        )
        db.session.add(e)

    # Deputies
    deps = [
        Deputy(full_name="Иванов Иван Иванович", faction="Единство", district="Округ №1", email="ivanov@example.com", phone="+7 900 111-22-33", bio="Опытный депутат с 2015 года.", photo_url="https://picsum.photos/seed/ivanov/400/250"),
        Deputy(full_name="Петров Петр Петрович", faction="Развитие", district="Округ №2", email="petrov@example.com", phone="+7 900 222-33-44", bio="Инициатор программ по благоустройству.", photo_url="https://picsum.photos/seed/petrov/400/250"),
        Deputy(full_name="Сидорова Анна Сергеевна", faction="Город", district="Округ №3", email="sidorova@example.com", phone="+7 900 333-44-55", bio="Эксперт по транспорту и экологии.", photo_url="https://picsum.photos/seed/sidorova/400/250"),
    ]
    db.session.add_all(deps)

    # FAQ
    faqs = [
        FAQ(question="Как подать обращение в городскую думу?", answer="Вы можете отправить обращение через официальный портал или приёмную.", is_published=True),
        FAQ(question="Где узнать о расписании заседаний?", answer="Посмотрите раздел «Календарь» на сайте.", is_published=True),
    ]
    db.session.add_all(faqs)

    db.session.commit()
    print("База данных инициализирована. Созданы admin@example.com / admin123")
