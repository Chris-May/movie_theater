import svcs

from movie.infrastructure.store import IEventStore


def test__add_showing__creates_event(app):
    # First create a movie to get a valid movie_id
    movie_response = app.test_client().post(
        "/movie", json={"name": "Inception", "duration": 148, "poster_url": "http://example.com/inception.jpg"}
    )
    movie_data = movie_response.get_json()
    movie_id = movie_data['movie_id']

    # Now create a showing for that movie
    response = app.test_client().post(
        "/showing", json={"movie_id": movie_id, "start_time": "2023-06-15T19:30:00", "available_seats": 100}
    )
    data = response.get_json()

    # Re-enter app context to access svcs.flask.get
    event_store = svcs.flask.get(IEventStore)
    events = event_store.load_stream(data['showing_id'])
    assert len(events) == 1

    # Verify the response contains the expected data
    assert data['movie_id'] == movie_id
    assert data['start_time'] == "2023-06-15T19:30:00"
    assert data['available_seats'] == 100  # noqa: PLR2004
