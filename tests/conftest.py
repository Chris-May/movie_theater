from pathlib import Path

import pytest_asyncio

from movie.web.entry import create_app


@pytest_asyncio.fixture(autouse=True)
async def app():
    testing_settings = Path(__file__).parent / 'testing.toml'
    assert testing_settings.exists()
    app = create_app(testing_settings)
    async with app.app_context():
        yield app
