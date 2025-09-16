from flask_admin.contrib.sqla import ModelView
from flask_login import current_user
from flask import redirect, url_for, request
from extensions import admin, db
from models import User, News, Document, Event, Deputy, FAQ

class SecureModelView(ModelView):
    can_view_details = True
    column_display_pk = True

    def is_accessible(self):
        return current_user.is_authenticated and current_user.is_admin

    def inaccessible_callback(self, name, **kwargs):
        return redirect(url_for('auth.login', next=request.url))

def init_admin(app):
    admin.init_app(app)

    admin.add_view(SecureModelView(
        User, db.session,
        category="Пользователи",
        endpoint="admin_users",     # <— уникально
        name="Пользователи"
    ))
    admin.add_view(SecureModelView(
        News, db.session,
        category="Контент",
        endpoint="admin_news",      # <— уникально (не 'news')
        name="Новости"
    ))
    admin.add_view(SecureModelView(
        Document, db.session,
        category="Контент",
        endpoint="admin_documents", # <— уникально
        name="Документы"
    ))
    admin.add_view(SecureModelView(
        Event, db.session,
        category="Контент",
        endpoint="admin_events",    # <— уникально
        name="События"
    ))
    admin.add_view(SecureModelView(
        Deputy, db.session,
        category="Контент",
        endpoint="admin_deputies",  # <— уникально
        name="Депутаты"
    ))
    admin.add_view(SecureModelView(
        FAQ, db.session,
        category="Контент",
        endpoint="admin_faq",       # <— уникально
        name="FAQ"
    ))
