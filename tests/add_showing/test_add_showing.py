import svcs

from movie.infrastructure.store import IEventStore


def test__add_showing__creates_event(app):
    # GIVEN a movie exists
    movie_response = app.test_client().post(
        "/movie", json={"name": "Inception", "duration": 148, "poster_url": "http://example.com/inception.jpg"}
    )
    movie_data = movie_response.get_json()
    movie_id = movie_data['movie_id']

    # WHEN we add a showing
    response = app.test_client().post(
        "/showing",
        json={
            "movie_id": movie_id,
            "start_time": "2023-06-15T19:30:00",
            "available_seats": ["A1", "A2", "A3", "B1", "B2", "B3"],
        },
    )
    data = response.get_json()

    # THEN we can see the event in the event store with the correct data
    event_store = svcs.flask.get(IEventStore)
    events = event_store.load_stream(data['showing_id'])
    assert len(events) == 1

    assert data['movie_id'] == movie_id
    assert data['start_time'] == "2023-06-15T19:30:00"
    assert data['available_seats'] == ["A1", "A2", "A3", "B1", "B2", "B3"]
