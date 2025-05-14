from uuid import UUID

import quart
from quart import request

from movie.domain.repos import ShowingRepo

bp = quart.Blueprint("reserve_ticket", __name__)


@bp.post('/showing/<string:showing_id>')
async def reserve_ticket(showing_id: str):
    showing = await ShowingRepo().get_showing(UUID(showing_id))
    available_seats = set(showing.available_seats)
    form = await request.form
    requested_seats = set(form.getlist("selected_seats"))
    if not requested_seats.issubset(available_seats):
        from sqlalchemy.orm import Session

        from movie import services
        from movie.slices.showing_detail.model import ShowingDetail

        session = services.get(Session)
        showing = session.query(ShowingDetail).filter_by(showing_id=showing_id).one_or_none()
        unavailable_seats = requested_seats - available_seats
        return await quart.render_template(
            'showing_detail.html', showing=showing, error=f'These seats are unavailable: {unavailable_seats}'
        )
    await showing.reserve_seats(form['user'], *requested_seats)
    return await quart.render_template(
        'thank_you.html', user=form['user'], selected_seats=requested_seats, start_time=showing.start_time
    )
