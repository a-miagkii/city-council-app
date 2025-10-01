from flask import Blueprint, render_template
from models import News, Event

bp = Blueprint('main', __name__)

@bp.route('/')
def index():
    news = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).limit(5).all()
    events = Event.query.filter_by(is_public=True).order_by(Event.start_time.asc()).limit(5).all()
    return render_template('index.html', news=news, events=events)

@bp.route('/about')
def about():
    return render_template('about.html')