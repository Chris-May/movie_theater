import flask
from flask import Request

bp = flask.Blueprint("reserve_ticket", __name__)


@bp.post('/showing/<string:showing_id>')
def reserve_ticket(request: Request):
    return request.form.getlist("selected_seats")
