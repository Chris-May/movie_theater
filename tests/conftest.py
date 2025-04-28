import sqlite3

import pytest
from eventsourcing.system import SingleThreadedRunner

from movie.domain.system import MovieSystem


@pytest.fixture
def runner(monkeypatch):
    monkeypatch.setenv('TEST', 'true')
    con = sqlite3.connect(':memory:')
    system = MovieSystem(con)
    runner = SingleThreadedRunner(system)

    runner.start()
    followers = [runner.apps.get(name) for name in set(runner.system.followers)]
    for follower in followers:
        if hasattr(follower, 'set_db'):
            follower.set_db(con)

    yield runner
    runner.stop()
