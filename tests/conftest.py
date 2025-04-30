import sqlite3

import pytest
from eventsourcing.projection import ProjectionRunner
from eventsourcing.system import SingleThreadedRunner
from eventsourcing.utils import Environment

from movie.domain.application import MovieApplication
from movie.domain.system import MovieSystem
from movie.slices.admin_available_movies.application import AvailableMovieView, AvailableMovieProjection


@pytest.fixture
def runner(monkeypatch):
    env = Environment()
    env['PERSISTENCE_MODULE'] = 'eventsourcing.sqlite'
    env['SQLITE_DBNAME'] = ':memory:'
    monkeypatch.setenv('TEST', 'true')
    system = MovieSystem()
    runner = SingleThreadedRunner(system, env=env)

    runner.start()
    followers = [runner.apps.get(name) for name in set(runner.system.followers)]
    for follower in followers:
        if hasattr(follower, 'set_db'):
            follower.set_db(con)

    yield runner
    runner.stop()
