"""
This module contains the business logic for the now playing page.
When a showing is added to the system, this module adds a new row to the now playing database.
When a ticket is reserved for a showing, this module updates the row in the now playing database.
"""

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from movie import services
from movie.domain import events
from movie.domain.model import Movie
from movie.infrastructure.store import Base, IEventStore


class NowPlayingReadModel(Base):
    __tablename__ = 'now_playing_read_model'

    showing_id = Column(String, primary_key=True)
    movie_id = Column(String, nullable=False)
    movie_title = Column(String, nullable=False)
    movie_poster_url = Column(String, nullable=False)
    showing_time = Column(DateTime, nullable=False)
    tickets_remaining = Column(Integer, nullable=False)

    def __repr__(self):
        return (
            '<NowPlayingReadModel '
            f'showing_id={self.showing_id}, '
            f'movie_title={self.movie_title}, '
            f'showing_time={self.showing_time}, '
            f'tickets_remaining={self.tickets_remaining} '
            '>'
        )


def on_new_showing(event: events.ShowingAdded):
    """
    This function is called when a new showing is added to the system.
    It updates the read model to power the now showing page.
    Each row in this database represents a movie showing.
    :param event:
    :return:
    """
    session, event_store = services.get(Session, IEventStore)
    showing_id = str(event.entity_id)

    # Check if showing already exists
    if session.query(NowPlayingReadModel).filter_by(showing_id=showing_id).first():
        msg = f"Showing {showing_id} already exists"
        raise ValueError(msg)

    # Get movie details from event store
    event_stream = event_store.load_stream(event.movie_id)
    if not event_stream:
        msg = f"Movie {event.movie_id} does not exist"
        raise ValueError(msg)
    movie = Movie(*event_stream)

    # Create new row in now playing read model
    row = NowPlayingReadModel(
        showing_id=showing_id,
        movie_id=str(event.movie_id),
        movie_title=movie.title,
        movie_poster_url=movie.poster_url,
        showing_time=event.start_time,
        tickets_remaining=len(event.available_seats),
    )
    session.add(row)
    session.commit()


def on_ticket_reserved(event: events.TicketReserved):
    """
    This function is called when a ticket is reserved for a showing.
    It updates the tickets_remaining count in the now playing read model.
    :param event:
    :return:
    """
    session = services.get(Session)
    showing_id = str(event.entity_id)

    # Get the showing from the read model
    row = session.query(NowPlayingReadModel).filter_by(showing_id=showing_id).first()
    if not row:
        msg = f"Showing {showing_id} does not exist"
        raise ValueError(msg)

    # Decrease tickets_remaining by 1
    if row.tickets_remaining <= 0:
        msg = f"No tickets remaining for showing {showing_id}"
        raise ValueError(msg)

    row.tickets_remaining -= 1
    session.commit()
