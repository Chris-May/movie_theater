import flask
from flask.typing import ResponseValue

from movie.domain.model import Movie

bp = flask.Blueprint("add_movie", __name__)


@bp.post("/movie")
def add_movie_endpoint() -> ResponseValue:
    data = flask.request.get_json()
    name = data.get("name")
    duration = data.get("duration")
    poster_url = data.get("poster_url")

    if not all([name, duration, poster_url]):
        return flask.make_response({"error": "Missing required fields"}, 400)

    movie = Movie.create(name=name, duration=duration, poster_url=poster_url)
    return flask.make_response(
        {
            "movie_id": str(movie.movie_id),
            "name": movie.title,
            "duration": movie.duration,
            "poster_url": movie.poster_url,
        },
        201,
    )
