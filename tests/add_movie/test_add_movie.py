from uuid import UUID

from movie.slices.add_movie.command import add_movie


def test__add_movie__returns_movie_id(runner):
    # WHEN we create a movie
    result = add_movie('dummy title', 100, 'https://dummy.com/poster.png', runner)
    # THEN we get a movie id
    assert isinstance(result, UUID)
