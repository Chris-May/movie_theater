import logging
from collections import defaultdict

import flask
from sqlalchemy.orm import Session

from movie import services
from movie.slices.now_playing import NowPlayingReadModel

logger = logging.getLogger(__name__)
bp = flask.Blueprint("view_now_showing", __name__)


@bp.get("/")
def list_now_playing():
    """
    This function renders HTML the list of movies that are currently showing.
    It retrieves showings from the 'now_playing_read_model' table in a way that groups
    them by movie and sorts them by showing time.
    """
    session = services.get(Session)
    showings = (
        session.query(NowPlayingReadModel)
        .order_by(NowPlayingReadModel.movie_title, NowPlayingReadModel.showing_time)
        .all()
    )
    logger.critical(showings)

    # Group showings by movie
    movies = defaultdict(list)
    for showing in showings:
        movies[showing.movie_title].append(showing)

    # Convert to list of tuples (movie_title, showings) and sort by movie title
    movies_list = sorted(movies.items())
    logger.info(movies_list)

    return flask.render_template("now_playing.html", movies=movies_list, count=len(showings))
