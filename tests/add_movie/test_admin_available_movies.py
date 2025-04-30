import dirty_equals as d
from eventsourcing.projection import ProjectionRunner

from movie.domain.application import MovieApplication
from movie.slices.admin_available_movies.application import AvailableMovieProjection, AvailableMovieView


def test__available_movies__when_movie_added__row_appears_in_database(runner):
    projector_runner = ProjectionRunner(application_class=MovieApplication, projection_class=AvailableMovieProjection, view_class=AvailableMovieView)
    # GIVEN a movie-added event
    movie_name = 'The Matrix'
    movie_poster_url = 'http://movie.com/poster.jpg'
    duration = 120
    app = runner.get(MovieApplication)

    # WHEN the system runs
    movie_id = app.add_movie(movie_name, duration, movie_poster_url)

    # THEN we can see the row in the available movies view
    admin_app = runner.get(AvailableMovieProjection)
    available_movies = admin_app.get_all()  # Use the projection's query method

    # Find the movie by ID
    available_movie = next((m for m in available_movies if str(m.movie_id) == str(movie_id)), None)
    assert available_movie is not None

    result = {
        'movie_id': available_movie.movie_id,
        'movie_name': available_movie.movie_name,
        'movie_poster': available_movie.movie_poster,
        'movie_duration': available_movie.movie_duration,
    }

    assert result == {
        'movie_id': d.IsUUID,
        'movie_name': movie_name,
        'movie_poster': movie_poster_url,
        'movie_duration': duration,
    }
