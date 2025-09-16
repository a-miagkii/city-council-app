# Учебное приложение «Городская дума» (Flask)

Базовый портал на Flask с авторизацией (пользователь/админ), админ-панелью, разделами: Новости, Календарь, Документы, Депутаты, FAQ, Поиск.

## Стек
- Flask, SQLAlchemy, Flask-Login, Flask-Migrate
- Flask-Admin для админки
- Bootstrap 5 (CDN) для адаптивной вёрстки
- SQLite по умолчанию (можно заменить на PostgreSQL, изменив `SQLALCHEMY_DATABASE_URI`)

## Запуск (локально)
1. Установите Python 3.11+.
2. Создайте и активируйте виртуальное окружение:
   ```bash
   python -m venv .venv
   # Windows
   .venv\Scripts\activate
   # Linux/Mac
   source .venv/bin/activate
   ```
3. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
4. (Опционально) Создайте `.env` на основе `.env.example` и при необходимости поменяйте конфиг.
5. Инициализируйте БД и наполните демо-данными:
   ```bash
   python seeds.py
   ```
   В консоли появится логин/пароль админа: `admin@example.com / admin123`.

6. Запустите приложение:
   ```bash
   python app.py
   ```
   Откройте: http://127.0.0.1:5000

7. Админ-панель: http://127.0.0.1:5000/admin

## Роли и доступ
- Роль `admin` получает доступ к админ-панели (Flask-Admin) и может создавать/редактировать записи.
- Роль `user` имеет чтение публичных разделов.

## Переключение на PostgreSQL
Установите переменную окружения:
```
SQLALCHEMY_DATABASE_URI=postgresql+psycopg2://user:pass@localhost:5432/city_council
```
и установите драйвер:
```
pip install psycopg2-binary
```

## Структура проекта
```
flask_city_council/
  app.py                # Factory + регистрация блюпринтов
  config.py             # Конфиги
  extensions.py         # Инициализация расширений
  models.py             # Модели БД
  admin.py              # Flask-Admin
  seeds.py              # Инициализация и демо-данные
  blueprints/           # Модули маршрутов
    auth/
    main/
    news/
    documents/
    events/
    deputies/
    faq/
    search/
  templates/            # Jinja2 шаблоны (Bootstrap 5)
  static/               # CSS/JS/изображения
  requirements.txt
  .env.example
```

## Заметки по поиску
Сейчас реализован простой полнотекстовый поиск по `LIKE`. Для улучшения можно:
- SQLite FTS5 (быстрая индексация в dev-режиме)
- PostgreSQL `tsvector`/`to_tsvector` для продвинутого поиска

## Безопасность и загрузка файлов
Для учебных целей документы хранят URL (`file_url`). В реальном проекте добавьте:
- форму и эндпоинт загрузки файлов с валидацией расширений и размеров;
- хранение в `/uploads` и раздачу через защищённые маршруты для приватных файлов.

## Лицензия
MIT.
