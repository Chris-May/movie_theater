import quart
from quart.typing import ResponseValue

from movie.domain.model import Movie

bp = quart.Blueprint("add_movie", __name__)


@bp.post("/movie")
async def add_movie_endpoint() -> ResponseValue:
    data = await quart.request.get_json()
    name = data.get("name")
    duration = data.get("duration")
    poster_url = data.get("poster_url")

    if not all([name, duration, poster_url]):
        return await quart.make_response({"error": "Missing required fields"}, 400)

    movie = await Movie.create(name=name, duration=duration, poster_url=poster_url)
    return await quart.make_response(
        {
            "movie_id": str(movie.movie_id),
            "name": movie.title,
            "duration": movie.duration,
            "poster_url": movie.poster_url,
        },
        201,
    )
