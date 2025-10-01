from datetime import datetime, timedelta
from extensions import db
from models import User, News, Document, Event, Deputy, FAQ
from app import create_app

def seed_db():
    app = create_app()

    with app.app_context():
        # Полная переинициализация БД
        db.drop_all()
        db.create_all()

        # Пользователи
        admin = User(email="admin@example.com", name="Администратор", role="admin")
        admin.set_password("admin123")
        user = User(email="user@example.com", name="Иван Пользователь", role="user")
        user.set_password("user123")

        db.session.add_all([admin, user])

        # Новости (сатира/вымысел)
        news_items = [
            {
                "title": "Кончилась американская лицензия: c 1 января 2026 года в России прекращается производство «Докторской» колбасы",
                "body": "Американский миллиардер Пол Рокфеллер отказался продлевать лицензию на производство «Докторской» колбасы, которая была приобретена наркомом пищевой промышленности СССР Анастасом Микояном в 1935 году.",
                "published_at": datetime.utcnow() - timedelta(hours=7),
            },
            {
                "title": "Сроки добровольной сдачи криптовалюты государству продлили до 1 января",
                "body": "Государство пошло навстречу гражданам и разрешило им добровольно сдать имеющуюся у них криптовалюту до 1 января 2026 года – в этом случае к владельцам активов не будут применены никакие санкции, связанные непосредственно с фактом владения цифровыми активами. Ранее дедлайн был установлен на 1 октября 2025 года, однако возможностью пока воспользовались немногие.",
                "published_at": datetime.utcnow() - timedelta(days=1, hours=3),
            },
            {
                "title": "ЦРУ: Китай построил 40-миллионный город из пенопласта для имитации экономического роста",
                "body": "Эксперты оценили благоустройство: лёгкий, экологичный и прекрасно держит плакаты. Минус один — при сильном ветре мегаполис переселяется в соседнюю провинцию.",
                "published_at": datetime.utcnow() - timedelta(days=2),
            },
            {
                "title": "Директор Guinness признался в многолетнем плевании в пиво, поставляемое в Россию",
                "body": "Директор пивоваренной компании Guinness Патрик О'Мэлли признался, что протяжении многих лет лично плевал в каждую партию пива, предназначенную для российского рынка. Своё решение он пояснил протестом против политики Кремля, а также сообщил, что ему такой ход подсказала бывшая жена.",
                "published_at": datetime.utcnow() - timedelta(days=3),
            },
            {
                "title": "За тёплую погоду в сентябре придётся заплатить налог",
                "body": "За аномально тёплую погоду в сентябре, наблюдающуюся в отдельных российских регионах, физическим лицам придётся заплатить дополнительный сбор – он составит от 422 до 1268 рублей в зависимости от места проживания, семейного статуса и ряда других параметров. Сейчас готовится соответствующий проект постановления правительства.",
                "published_at": datetime.utcnow() - timedelta(days=4),
            },
        ]

        # Способ 1: добавить внутри цикла
        for item in news_items:
            n = News(
                title=item["title"],
                body=item["body"],
                published_at=item["published_at"],
                created_by=admin,        # если это relationship — ок
                is_published=True,
            )
            db.session.add(n)

        # === Альтернатива (закомментировано): разом через add_all ===
        # news_records = [
        #     News(
        #         title=i["title"],
        #         body=i["body"],
        #         published_at=i["published_at"],
        #         created_by=admin,
        #         is_published=True,
        #     ) for i in news_items
        # ]
        # db.session.add_all(news_records)

        # Документы
        docs = [
            Document(title="Постановление о бюджете", summary="Утверждение бюджета на 2025 год.", doc_type="постановление", file_url="#"),
            Document(title="Проект закона о транспорте", summary="Проект по развитию общественного транспорта.", doc_type="проект", file_url="#"),
            Document(title="Решение о благоустройстве", summary="Программа благоустройства дворов.", doc_type="решение", file_url="#"),
        ]
        db.session.add_all(docs)

        # События
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

        # Депутаты
        deps = [
            Deputy(full_name="Иванов Иван Иванович", faction="Единство", district="Округ №1",
                   email="ivanov@example.com", phone="+7 900 111-22-33",
                   bio="Опытный депутат с 2015 года.",
                   photo_url="https://www.menslife.com/upload/iblock/7c4/1_c8amosn.jpg"),
            Deputy(full_name="Петров Петр Петрович", faction="Развитие", district="Округ №2",
                   email="petrov@example.com", phone="+7 900 222-33-44",
                   bio="Инициатор программ по благоустройству.",
                   photo_url="https://www.pravilamag.ru/upload/img_cache/ee2/ee2ff72536feacd5730b82c510617016_ce_5049x3366x24x0_cropped_510x340.webp"),
            Deputy(full_name="Сидорова Анна Сергеевна", faction="Город", district="Округ №3",
                   email="sidorova@example.com", phone="+7 900 333-44-55",
                   bio="Эксперт по транспорту и экологии.",
                   photo_url="https://www.ok-magazine.ru/images/cache/2012/11/21/fit_455_547_false_crop_475_570_0_0_q90_298021_05895199f8835e502c7fc1e34.jpeg"),
        ]
        db.session.add_all(deps)

        # FAQ
        faqs = [
            FAQ(question="Как подать обращение в городскую думу?",
                answer="Вы можете отправить обращение через официальный портал или приёмную.",
                is_published=True),
            FAQ(question="Где узнать о расписании заседаний?",
                answer="Посмотрите раздел «Календарь» на сайте.",
                is_published=True),
        ]
        db.session.add_all(faqs)

        # Коммит
        db.session.commit()
        print("База данных инициализирована. Созданы admin@example.com / admin123")

if __name__ == "__main__":
    seed_db()
