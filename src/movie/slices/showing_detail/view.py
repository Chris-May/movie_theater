import asyncio
import json

import quart
from datastar_py import ServerSentEventGenerator
from datastar_py.quart import make_datastar_response
from quart import current_app, request
from sqlalchemy.orm import Session

from movie import services
from movie.domain.model import UserID
from movie.slices.showing_detail.model import ShowingDetail

bp = quart.Blueprint('detail_showing_view', __name__)


@bp.get('/showing/<string:showing_id>')
async def showing_detail(showing_id):
    selected_seats, showing, user_id, _ = await showing_info(showing_id)
    return await quart.render_template(
        'showing_detail.html', showing=showing, user_id=user_id, selected_seats=selected_seats
    )


async def get_showing(showing_id):
    session = services.get(Session)
    showing = session.query(ShowingDetail).filter_by(showing_id=showing_id).one_or_none()
    user_id = services.get(UserID)
    return showing, user_id


async def showing_info(showing_id):
    showing, user_id = await get_showing(showing_id)
    datastar_stuff = json.loads((await request.values).get('datastar', '{}'))
    selected_seats = {key for key, val in datastar_stuff.get('selected-seats', {}).items() if val} - set(
        showing.reserved_seats
    )
    return selected_seats, showing, user_id, showing.reserved_seats


@bp.get('/showing/<string:showing_id>/updates')
async def detail_updates(showing_id):
    app = current_app._get_current_object()  # noqa: SLF001

    async def updates():
        while True:
            async with app.app_context():
                showing, _ = await get_showing(showing_id)
                yield ServerSentEventGenerator.merge_signals(dict(reservedSeats=showing.reserved_seats))
                await asyncio.sleep(10)

    response = await make_datastar_response(updates())
    response.timeout = None
    return response
