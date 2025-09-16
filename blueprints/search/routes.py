from flask import Blueprint, render_template, request
from models import News, Document, Deputy, FAQ
from sqlalchemy import or_

bp = Blueprint('search', __name__, url_prefix='/search')

@bp.route('/')
def search():
    q = request.args.get('q', '').strip()
    news = docs = deputies = faqs = []
    if q:
        news = News.query.filter(
            or_(News.title.ilike(f'%{q}%'), News.body.ilike(f'%{q}%'))
        ).all()
        docs = Document.query.filter(
            or_(Document.title.ilike(f'%{q}%'), Document.summary.ilike(f'%{q}%'))
        ).all()
        deputies = Deputy.query.filter(
            or_(Deputy.full_name.ilike(f'%{q}%'), Deputy.bio.ilike(f'%{q}%'))
        ).all()
        faqs = FAQ.query.filter(
            or_(FAQ.question.ilike(f'%{q}%'), FAQ.answer.ilike(f'%{q}%'))
        ).all()
    return render_template('search/results.html', q=q, news=news, docs=docs, deputies=deputies, faqs=faqs)
