from flask import Blueprint, render_template
from models import Document

bp = Blueprint('documents', __name__, url_prefix='/documents')

@bp.route('/')
def list_documents():
    items = Document.query.filter_by(is_published=True).order_by(Document.published_at.desc()).all()
    return render_template('documents/list.html', items=items)
