import pytest
import svcs

from movie.infrastructure.store import IEventStore


@pytest.mark.asyncio
async def test__add_movie__creates_event(app):
    test_client = app.test_client()
    response = await test_client.post(
        "/movie", json={"name": "Inception", "duration": 148, "poster_url": "http://example.com/inception.jpg"}
    )
    data = await response.get_json()
    # Re-enter app context to access svcs.quart.get
    event_store = svcs.quart.get(IEventStore)
    events = event_store.load_stream(data['movie_id'])
    assert len(events) == 1
