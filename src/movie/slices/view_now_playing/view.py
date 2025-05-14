import logging
from collections import defaultdict
from datetime import datetime, time

import quart
from sqlalchemy.orm import Session

from movie import services
from movie.slices.now_playing import NowPlayingReadModel

logger = logging.getLogger(__name__)
bp = quart.Blueprint("view_now_showing", __name__)


@bp.get("/")
async def list_now_playing():
    """
    This function renders HTML the list of movies that are currently showing.
    It retrieves showings from the 'now_playing_read_model' table in a way that groups
    them by movie and sorts them by showing time.
    """
    session = services.get(Session)
    today = datetime.now().date()  # noqa: DTZ005
    tomorrow = datetime.combine(today, time.max)
    showings = (
        session.query(NowPlayingReadModel)
        .filter(
            NowPlayingReadModel.showing_time >= today,
            NowPlayingReadModel.showing_time < tomorrow,
        )
        .order_by(NowPlayingReadModel.movie_title, NowPlayingReadModel.showing_time)
        .all()
    )

    # Group showings by movie
    movies = defaultdict(list)
    for showing in showings:
        movies[showing.movie_title].append(showing)

    # Convert to list of tuples (movie_title, showings) and sort by movie title
    movies_list = sorted(movies.items())

    return await quart.render_template("now_playing.html", movies=movies_list, count=len(showings))
