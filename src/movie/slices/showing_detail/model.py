import itertools as it
from collections.abc import Iterable

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from movie import services
from movie.domain import events
from movie.domain.model import Movie
from movie.infrastructure.store import Base, IEventStore


class ShowingDetail(Base):
    __tablename__ = 'showing_detail'
    showing_id = Column(String, primary_key=True)
    movie_name = Column(String, nullable=False)
    poster_url = Column(String, nullable=False)
    duration = Column(Integer, nullable=False)
    start_time = Column(DateTime, nullable=False)
    available_seats = Column(String, nullable=False)  # comma-separated
    reserved_seats = Column(String, nullable=False)  # comma-separated
    all_seats = Column(String, nullable=False)  # comma-separated

    def __repr__(self):
        return (
            '<ShowingDetail '
            f'showing_id={self.showing_id}, '
            f'movie_name={self.movie_name}, '
            f'available_seat_count={len(self.available_seats)}, '
            f'reserved_seat_count={len(self.reserved_seats)} '
            '>'
        )

    @staticmethod
    def seats_to_str(seats):
        return ','.join(seats)

    @staticmethod
    def str_to_seats(seats_str):
        return [s for s in seats_str.split(',') if s]

    @property
    def all_seat_list(self) -> list[str]:
        return self.all_seats.split(',')

    @property
    def available(self) -> set[str]:
        return set(self.available_seats.split(','))

    @property
    def reserved(self) -> set[str]:
        return set(self.reserved_seats.split(','))

    @property
    def rows(self) -> Iterable[tuple[str, Iterable[str]]]:
        return it.groupby(self.all_seat_list, lambda x: x[0])

    def seat_is_available(self, seat: str):
        return seat in self.available


def handle_showing_added(event: events.ShowingAdded):
    session, event_store = services.get(Session, IEventStore)
    showing_id = str(event.entity_id)
    if session.query(ShowingDetail).filter_by(showing_id=showing_id).first():
        msg = f"Showing {showing_id} already exists"
        raise ValueError(msg)
    all_seats = event.available_seats
    movie = Movie(*event_store.load_stream(event.movie_id))

    row = ShowingDetail(
        showing_id=showing_id,
        movie_name=movie.title,
        poster_url=movie.poster_url,
        duration=movie.duration,
        start_time=event.start_time,
        available_seats=ShowingDetail.seats_to_str(all_seats),
        reserved_seats='',
        all_seats=ShowingDetail.seats_to_str(all_seats),
    )
    session.add(row)
    session.commit()


def handle_ticket_reserved(event: events.TicketReserved):
    session = services.get(Session)
    showing_id = str(event.showing_id)
    row = session.query(ShowingDetail).filter_by(showing_id=showing_id).first()
    if not row:
        msg = f"Showing {showing_id} does not exist"
        raise ValueError(msg)
    seat = event.seat_id
    available = ShowingDetail.str_to_seats(row.available_seats)
    reserved = ShowingDetail.str_to_seats(row.reserved_seats)
    if seat not in available:
        msg = f"Seat {seat} is not available for showing {showing_id}"
        raise ValueError(msg)
    available.remove(seat)
    reserved.append(seat)
    row.available_seats = ShowingDetail.seats_to_str(available)
    row.reserved_seats = ShowingDetail.seats_to_str(reserved)
    session.commit()


def handle_ticket_cancelled(event: events.TicketCancelled):
    session = services.get(Session)
    showing_id = str(event.showing_id)
    row = session.query(ShowingDetail).filter_by(showing_id=showing_id).first()
    if not row:
        msg = f"Showing {showing_id} does not exist"
        raise ValueError(msg)
    seat = event.seat_id
    available = ShowingDetail.str_to_seats(row.available_seats)
    reserved = ShowingDetail.str_to_seats(row.reserved_seats)
    if seat not in reserved:
        msg = f"Seat {seat} is not reserved for showing {showing_id}"
        raise ValueError(msg)
    reserved.remove(seat)
    available.append(seat)
    row.available_seats = ShowingDetail.seats_to_str(available)
    row.reserved_seats = ShowingDetail.seats_to_str(reserved)
    session.commit()
