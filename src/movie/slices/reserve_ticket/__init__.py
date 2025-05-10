from uuid import UUID

import flask
from flask import request

from movie.domain.repos import ShowingRepo

bp = flask.Blueprint("reserve_ticket", __name__)


@bp.post('/showing/<string:showing_id>')
def reserve_ticket(showing_id: str):
    showing = ShowingRepo().get_showing(UUID(showing_id))
    available_seats = set(showing.available_seats)
    requested_seats = set(request.form.getlist("selected_seats"))
    if not requested_seats.issubset(available_seats):
        from sqlalchemy.orm import Session

        from movie import services
        from movie.slices.showing_detail.model import ShowingDetail

        session = services.get(Session)
        showing = session.query(ShowingDetail).filter_by(showing_id=showing_id).one_or_none()
        unavailable_seats = requested_seats - available_seats
        return flask.render_template(
            'showing_detail.html', showing=showing, error=f'These seats are unavailable: {unavailable_seats}'
        )
    showing.reserve_seats(request.form['user'], *requested_seats)
    return dict(
        seats=request.form.getlist("selected_seats"),
        showing=showing_id,
        form=request.form,
        user=request.form['user'],
        available_seats=showing.available_seats,
    )
