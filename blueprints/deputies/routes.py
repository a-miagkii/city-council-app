from flask import Blueprint, render_template
from models import Deputy

bp = Blueprint('deputies', __name__, url_prefix='/deputies')

@bp.route('/')
def list_deputies():
    items = Deputy.query.order_by(Deputy.full_name.asc()).all()
    return render_template('deputies/list.html', items=items)

@bp.route('/<int:deputy_id>')
def detail(deputy_id):
    item = Deputy.query.get_or_404(deputy_id)
    return render_template('deputies/detail.html', item=item)
