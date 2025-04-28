import dirty_equals as d

from movie.domain.application import MovieApplication
from movie.slices.admin_available_movies.application import AdminAvailableMovies


def test__available_movies__when_movie_added__row_appears_in_database(runner):
    # GIVEN a movie-added event
    movie_name = 'The Matrix'
    movie_poster_url = 'http://movie.com/poster.jpg'
    duration = 120
    app = runner.get(MovieApplication)

    # WHEN the system runs
    movie_id = app.add_movie(movie_name, duration, movie_poster_url)

    # THEN we can see the row in the database with the expected data
    admin_app = runner.get(AdminAvailableMovies)
    available_movie = admin_app.get_available_movie(movie_id)

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
