import asyncio

import quart
from datastar_py import ServerSentEventGenerator
from datastar_py.quart import make_datastar_response
from quart import current_app
from sqlalchemy.orm import Session

from movie import services
from movie.domain.model import UserID
from movie.slices.showing_detail.model import ShowingDetail

bp = quart.Blueprint('detail_showing_view', __name__)


@bp.get('/showing/<string:showing_id>')
async def showing_detail(showing_id):
    user_id = services.get(UserID)
    showing = await get_showing(showing_id)
    return await quart.render_template('showing_detail.html', showing=showing, user_id=user_id)


async def get_showing(showing_id) -> ShowingDetail:
    session = services.get(Session)
    return session.query(ShowingDetail).filter_by(showing_id=showing_id).scalar()


@bp.get('/showing/<string:showing_id>/updates')
async def detail_updates(showing_id):
    app = current_app._get_current_object()  # noqa: SLF001

    async def updates():
        while True:
            async with app.app_context():
                showing = await get_showing(showing_id)
                yield ServerSentEventGenerator.merge_signals(dict(reservedSeats=showing.reserved_seats))
                await asyncio.sleep(1)

    response = await make_datastar_response(updates())
    response.timeout = None
    return response
