import svcs

from movie.entry import create_app
from movie.infrastructure.store import IEventStore


def test__add_movie__creates_event():
    app = create_app('test.cfg')
    with app.app_context():
        response = app.test_client().post(
            "/movie", json={"name": "Inception", "duration": 148, "poster_url": "http://example.com/inception.jpg"}
        )
        data = response.get_json()
        # Re-enter app context to access svcs.flask.get
        event_store = svcs.flask.get(IEventStore)
        events = event_store.load_stream(data['movie_id'])
        assert len(events) == 1
