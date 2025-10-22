from flask import Blueprint, render_template, abort
from extensions import db
from models import News

bp = Blueprint('news', __name__, url_prefix='/news')

@bp.route('/')
def list_news():
    items = News.query.filter_by(is_published=True).order_by(News.published_at.desc()).all()
    return render_template('news/list.html', items=items)

@bp.route('/<int:news_id>')
def detail(news_id):
    item = db.session.get(News, news_id)
    if item is None or not item.is_published:
        abort(404)
    return render_template('news/detail.html', item=item)
