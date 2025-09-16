from flask import Blueprint, render_template
from models import Event

bp = Blueprint('events', __name__, url_prefix='/events')

@bp.route('/')
def list_events():
    items = Event.query.filter_by(is_public=True).order_by(Event.start_time.asc()).all()
    return render_template('events/list.html', items=items)
