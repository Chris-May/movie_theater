import asyncio
import json

import quart
from datastar_py import ServerSentEventGenerator
from datastar_py.consts import FragmentMergeMode
from datastar_py.quart import make_datastar_response
from quart import current_app, request
from sqlalchemy.orm import Session

from movie import services
from movie.domain.model import UserID
from movie.slices.showing_detail.model import ShowingDetail

bp = quart.Blueprint('detail_showing_view', __name__)


@bp.get('/showing/<string:showing_id>')
async def load_page(showing_id):
    user_id = services.get(UserID)
    showing = await get_showing(showing_id)
    return await quart.render_template('showing_detail.html', showing=showing, user_id=user_id)


@bp.get('/showing/<string:showing_id>/seats')
async def on_seat_selection(showing_id):
    app = current_app._get_current_object()  # noqa: SLF001
    # Get the data once before entering the streaming context
    initial_selected = json.loads(request.args.get('seats'))

    async def stream_updates():
        selected_seats = initial_selected

        for _ in range(1):
            async with app.app_context():
                showing = await get_showing(showing_id)
                reserved_seats = showing.reserved_seats or []

                # Filter out any selected seats that are now reserved
                valid_selected = [seat for seat in selected_seats if seat not in reserved_seats]

                yield ServerSentEventGenerator.merge_signals(
                    {
                        'selectedSeats': valid_selected,
                    }
                )
                content = (
                    "<ul id=seat-list>"
                    f"{''.join([f'<li id="selected-{seat}">{seat}</li>' for seat in valid_selected])}"
                    "</ul>"
                )
                yield ServerSentEventGenerator.merge_fragments(
                    content, selector='#seat-list', merge_mode=FragmentMergeMode.OUTER
                )
                await asyncio.sleep(2)

    return await make_datastar_response(stream_updates())


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
                reserved_ids = ', '.join(f'#selected-{seat}' for seat in showing.reserved_list)
                yield ServerSentEventGenerator.remove_fragments(reserved_ids)
                await asyncio.sleep(1)

    response = await make_datastar_response(updates())
    response.timeout = None
    return response
