import json

import flask
from flask import Response, request
from sqlalchemy.orm import Session

from movie import services
from movie.domain.model import UserID
from movie.slices.showing_detail.model import ShowingDetail

bp = flask.Blueprint('detail_showing_view', __name__)


@bp.get('/showing/<string:showing_id>')
def showing_detail(showing_id):
    session = services.get(Session)
    showing = session.query(ShowingDetail).filter_by(showing_id=showing_id).one_or_none()
    user_id = services.get(UserID)
    datastar_stuff = json.loads(request.values.get('datastar', '{}'))
    selected_seats = {key for key, val in datastar_stuff.get('selected-seats', {}).items() if val} - set(
        showing.reserved_seats
    )
    content = flask.render_template(
        'showing_detail.html', showing=showing, user_id=user_id, selected_seats=selected_seats
    )
    response = Response(content)
    response.headers['HX-Trigger-After-Swap'] = '{"updateSeats": {"target": "#seats"}}'
    return response
