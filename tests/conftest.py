import pytest
from eventsourcing.system import SingleThreadedRunner

from movie.domain import system


@pytest.fixture
def runner():
    runner = SingleThreadedRunner(system)
    runner.start()
    yield runner
    runner.stop()
