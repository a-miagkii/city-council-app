from flask import Flask
from config import DevConfig
from extensions import db, migrate, login_manager
from models import User
from admin import init_admin

# Blueprints
from blueprints.main.routes import bp as main_bp
from blueprints.auth.routes import bp as auth_bp
from blueprints.news.routes import bp as news_bp
from blueprints.documents.routes import bp as docs_bp
from blueprints.events.routes import bp as events_bp
from blueprints.deputies.routes import bp as deps_bp
from blueprints.faq.routes import bp as faq_bp
from blueprints.search.routes import bp as search_bp

def create_app(config_object=DevConfig):
    app = Flask(__name__)
    app.config.from_object(config_object)

    # Init extensions
    db.init_app(app)
    migrate.init_app(app, db)

    login_manager.init_app(app)
    login_manager.login_view = "auth.login"
    login_manager.login_message = "Требуется авторизация для доступа к этой странице."

    # Blueprints
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp)
    app.register_blueprint(news_bp)
    app.register_blueprint(docs_bp)
    app.register_blueprint(events_bp)
    app.register_blueprint(deps_bp)
    app.register_blueprint(faq_bp)
    app.register_blueprint(search_bp)

    # Admin
    init_admin(app)

    @app.context_processor
    def inject_globals():
        return dict()

    @app.shell_context_processor
    def make_shell_context():
        from models import News, Document, Event, Deputy, FAQ
        return dict(db=db, User=User, News=News, Document=Document, Event=Event, Deputy=Deputy, FAQ=FAQ)

    @app.route('/healthz')
    def healthz():
        return {"status": "ok"}

    return app

if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
