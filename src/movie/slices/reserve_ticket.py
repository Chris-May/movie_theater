import flask
from flask import request

bp = flask.Blueprint("reserve_ticket", __name__)


@bp.post('/showing/<string:showing_id>')
def reserve_ticket(showing_id: str):
    return dict(
        seats=request.form.getlist("selected_seats"), showing=showing_id, form=request.form, user=request.form['user']
    )
