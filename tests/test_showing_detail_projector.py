import random

import svcs
from sqlalchemy.orm import Session

import movie.slices.showing_detail.model as showing_detail_model
from movie.domain.model import Movie
from movie.infrastructure.store import IEventStore
from tests.factories import MovieAddedFactory, ShowingAddedFactory, TicketReservedFactory


def test__showing_added__creates_row():
    # GIVEN a projector and a ShowingAdded event
    session, event_store = svcs.flask.get(Session, IEventStore)
    movie_created = MovieAddedFactory.build()
    movie = Movie(movie_created)
    event_store.save(movie_created)
    event = ShowingAddedFactory.build(movie_id=movie.movie_id)

    # WHEN the event is handled
    showing_detail_model.handle_showing_added(event)

    # THEN a row is created with correct data
    row = session.query(showing_detail_model.ShowingDetail).filter_by(showing_id=str(event.entity_id)).first()
    assert row is not None
    assert row.movie_name == movie.title
    assert row.poster_url == movie.poster_url
    assert row.duration == movie.duration
    assert row.start_time == event.start_time
    assert row.available_seats == ','.join(event.available_seats)
    assert row.reserved_seats == ""
    assert row.all_seats == ','.join(event.available_seats)


def test__ticket_reserved__moves_seat():
    # GIVEN a showing row and a TicketReserved showing_added
    session, event_store = svcs.flask.get(Session, IEventStore)
    movie_created = MovieAddedFactory.build()
    movie = Movie(movie_created)
    event_store.save(movie_created)
    showing_added = ShowingAddedFactory.build(movie_id=movie.movie_id)
    event_store.save(movie_created, showing_added)
    showing_detail_model.handle_showing_added(showing_added)

    # When we reserve a seat
    seat = random.choice(showing_added.available_seats)  # noqa: S311
    reserve_event = TicketReservedFactory.build(entity_id=showing_added.entity_id, seat_id=seat)
    showing_detail_model.handle_ticket_reserved(reserve_event)

    # THEN the seat is moved to reserved
    row = session.query(showing_detail_model.ShowingDetail).filter_by(showing_id=str(showing_added.entity_id)).first()
    assert seat not in set(row.available_seats.split(","))
    assert row.reserved_seats == seat
