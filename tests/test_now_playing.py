import pytest
import svcs
from sqlalchemy.orm import Session

from movie.domain.model import Movie
from movie.infrastructure.store import IEventStore
from movie.slices.now_playing import NowPlayingReadModel, on_new_showing, on_ticket_reserved
from tests.factories import MovieAddedFactory, ShowingAddedFactory, TicketReservedFactory


class TestNowPlaying:
    def test_on_new_showing_creates_read_model(self):
        # Arrange
        session, event_store = svcs.flask.get(Session, IEventStore)
        movie_created = MovieAddedFactory.build()
        movie = Movie(movie_created)
        showing_added_event = ShowingAddedFactory.build(movie_id=movie.movie_id)
        event_store.save(movie_created, showing_added_event)

        # Act
        on_new_showing(showing_added_event)

        # Assert
        row = session.query(NowPlayingReadModel).filter_by(showing_id=str(showing_added_event.entity_id)).first()
        assert row is not None
        assert row.movie_id == str(movie.movie_id)
        assert row.movie_title == movie.title
        assert row.movie_poster_url == movie.poster_url
        assert row.showing_time == showing_added_event.start_time
        assert row.tickets_remaining == len(showing_added_event.available_seats)

    def test_on_new_showing_raises_error_if_showing_exists(self):
        # Arrange
        session, event_store = svcs.flask.get(Session, IEventStore)
        movie_created = MovieAddedFactory.build()
        movie = Movie(movie_created)
        showing_added_event = ShowingAddedFactory.build(movie_id=movie.movie_id)
        event_store.save(movie_created, showing_added_event)

        on_new_showing(showing_added_event)

        # Act & Assert
        with pytest.raises(ValueError, match=f"Showing {showing_added_event.entity_id} already exists"):
            on_new_showing(showing_added_event)

    def test_on_new_showing_raises_error_if_movie_not_found(self):
        # Arrange
        showing_added_event = ShowingAddedFactory.build()

        # Act & Assert
        with pytest.raises(ValueError, match=f"Movie {showing_added_event.movie_id} does not exist"):
            on_new_showing(showing_added_event)

    def test_on_ticket_reserved_decreases_tickets_remaining(self):
        # Arrange
        session, event_store = svcs.flask.get(Session, IEventStore)
        movie_created = MovieAddedFactory.build()
        movie = Movie(movie_created)
        showing_added_event = ShowingAddedFactory.build(movie_id=movie.movie_id)
        event_store.save(movie_created, showing_added_event)

        on_new_showing(showing_added_event)
        initial_tickets = (
            session.query(NowPlayingReadModel)
            .filter_by(showing_id=str(showing_added_event.entity_id))
            .first()
            .tickets_remaining
        )

        # Act
        ticket_reserved_event = TicketReservedFactory.build(entity_id=showing_added_event.entity_id)
        on_ticket_reserved(ticket_reserved_event)

        # Assert
        row = session.query(NowPlayingReadModel).filter_by(showing_id=str(showing_added_event.entity_id)).first()
        assert row.tickets_remaining == initial_tickets - 1

    def test_on_ticket_reserved_raises_error_if_showing_not_found(self):
        # Arrange
        ticket_reserved_event = TicketReservedFactory.build()

        # Act & Assert
        with pytest.raises(ValueError, match=f"Showing {ticket_reserved_event.showing_id} does not exist"):
            on_ticket_reserved(ticket_reserved_event)

    def test_on_ticket_reserved_raises_error_if_no_tickets_remaining(self):
        # Arrange
        session, event_store = svcs.flask.get(Session, IEventStore)
        movie_created = MovieAddedFactory.build()
        movie = Movie(movie_created)
        showing_added_event = ShowingAddedFactory.build(movie_id=movie.movie_id)
        event_store.save(movie_created, showing_added_event)

        on_new_showing(showing_added_event)

        # Reserve all tickets
        for seat in showing_added_event.available_seats:
            event = TicketReservedFactory.build(entity_id=showing_added_event.entity_id, seat_id=seat)
            on_ticket_reserved(event)

        # Try to reserve one more ticket
        extra_ticket = TicketReservedFactory.build(
            entity_id=showing_added_event.entity_id,
            seat_id="Z99",  # Non-existent seat
        )

        # Act & Assert
        with pytest.raises(ValueError, match=f"No tickets remaining for showing {showing_added_event.entity_id}"):
            on_ticket_reserved(extra_ticket)
