from datetime import datetime
from uuid import uuid4

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.movie.slices.showing_detail import Base, ShowingDetail, ShowingDetailProjector


class DummyEvent:
    pass


def make_session():
    engine = create_engine('sqlite:///:memory:')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)()


def test__showing_added__creates_row():
    # GIVEN a projector and a ShowingAdded event
    session = make_session()
    projector = ShowingDetailProjector(session)
    event = DummyEvent()
    event.entity_id = uuid4()
    event.movie_name = "Inception"
    event.movie_poster = "http://example.com/inception.jpg"
    event.duration = 148
    event.start_time = datetime(2023, 6, 15, 19, 30)
    event.available_seats = ["A1", "A2", "A3"]

    # WHEN the event is handled
    projector.handle_showing_added(event)

    # THEN a row is created with correct data
    row = session.query(ShowingDetail).filter_by(showing_id=str(event.entity_id)).first()
    assert row is not None
    assert row.movie_name == "Inception"
    assert row.poster_url == "http://example.com/inception.jpg"
    assert row.duration == 148  # noqa: PLR2004
    assert row.start_time == datetime(2023, 6, 15, 19, 30)
    assert row.available_seats == "A1,A2,A3"
    assert row.reserved_seats == ""
    assert row.all_seats == "A1,A2,A3"


def test__ticket_reserved__moves_seat():
    # GIVEN a showing row and a TicketReserved event
    session = make_session()
    projector = ShowingDetailProjector(session)
    # Add showing
    event = DummyEvent()
    event.entity_id = uuid4()
    event.movie_name = "Inception"
    event.movie_poster = "http://example.com/inception.jpg"
    event.duration = 148
    event.start_time = datetime(2023, 6, 15, 19, 30)
    event.available_seats = ["A1", "A2", "A3"]
    projector.handle_showing_added(event)
    # Reserve seat A2
    reserve_event = DummyEvent()
    reserve_event.showing_id = event.entity_id
    reserve_event.seat_id = "A2"
    projector.handle_ticket_reserved(reserve_event)
    # THEN A2 is moved from available to reserved
    row = session.query(ShowingDetail).filter_by(showing_id=str(event.entity_id)).first()
    assert set(row.available_seats.split(",")) == {"A1", "A3"}
    assert set(row.reserved_seats.split(",")) == {"A2"}


def test__ticket_cancelled__moves_seat_back():
    # GIVEN a showing row with a reserved seat and a TicketCancelled event
    session = make_session()
    projector = ShowingDetailProjector(session)
    # Add showing
    event = DummyEvent()
    event.entity_id = uuid4()
    event.movie_name = "Inception"
    event.movie_poster = "http://example.com/inception.jpg"
    event.duration = 148
    event.start_time = datetime(2023, 6, 15, 19, 30)
    event.available_seats = ["A1", "A2", "A3"]
    projector.handle_showing_added(event)
    # Reserve seat A2
    reserve_event = DummyEvent()
    reserve_event.showing_id = event.entity_id
    reserve_event.seat_id = "A2"
    projector.handle_ticket_reserved(reserve_event)
    # Cancel seat A2
    cancel_event = DummyEvent()
    cancel_event.showing_id = event.entity_id
    cancel_event.seat_id = "A2"
    projector.handle_ticket_cancelled(cancel_event)
    # THEN A2 is back in available, not in reserved
    row = session.query(ShowingDetail).filter_by(showing_id=str(event.entity_id)).first()
    assert set(row.available_seats.split(",")) == {"A1", "A2", "A3"}
    assert row.reserved_seats == ""
