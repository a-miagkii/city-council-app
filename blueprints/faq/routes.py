from flask import Blueprint, render_template
from models import FAQ

bp = Blueprint('faq', __name__, url_prefix='/faq')

@bp.route('/')
def list_faq():
    items = FAQ.query.filter_by(is_published=True).all()
    return render_template('faq/list.html', items=items)
