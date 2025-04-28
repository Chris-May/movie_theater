from urllib.parse import urlparse

from eventsourcing.system import Runner

from movie.domain.application import MovieApplication


def add_movie(name, duration, poster_url, runner: Runner):
    name = str(name)
    duration = int(duration)
    poster_url = urlparse(poster_url).geturl()
    app = runner.get(MovieApplication)
    return app.add_movie(name, duration, poster_url)
