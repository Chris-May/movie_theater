from datetime import datetime
from uuid import UUID

import quart
from quart.typing import ResponseValue

from movie.domain.model import Showing

bp = quart.Blueprint("add_showing", __name__)


@bp.post("/showing")
async def add_showing_endpoint() -> ResponseValue:
    data = await quart.request.get_json()
    movie_id = data.get("movie_id")
    start_time = data.get("start_time")
    available_seats = data.get("available_seats")

    if not all([movie_id, start_time, available_seats]):
        return await quart.make_response({"error": "Missing required fields"}, 400)

    try:
        movie_id = UUID(movie_id)
    except (ValueError, TypeError):
        return await quart.make_response({"error": "Invalid movie_id format"}, 400)

    try:
        start_time = datetime.fromisoformat(start_time)
    except ValueError:
        return await quart.make_response({"error": "start_time must be ISO 8601 format"}, 400)

    if not isinstance(available_seats, list) or not all(isinstance(seat, str) for seat in available_seats):
        return await quart.make_response({"error": "Available seats must be a list of strings"}, 400)

    showing = await Showing.create(movie_id=movie_id, start_time=start_time, available_seats=available_seats)
    return await quart.make_response(
        {
            "showing_id": str(showing.showing_id),
            "movie_id": str(showing.movie_id),
            "start_time": showing.start_time.isoformat(),
            "available_seats": showing.available_seats,
        },
        201,
    )
