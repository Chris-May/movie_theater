from pathlib import Path

import pytest

from movie.web.entry import create_app


@pytest.fixture(autouse=True)
def app():
    testing_settings = Path(__file__).parent / 'testing.toml'
    assert testing_settings.exists()
    app = create_app(testing_settings)
    with app.app_context():
        yield app
