from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session

from movie.domain import events

Base = declarative_base()


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

    @staticmethod
    def seats_to_str(seats):
        return ','.join(seats)

    @staticmethod
    def str_to_seats(seats_str):
        return [s for s in seats_str.split(',') if s]


class ShowingDetailProjector:
    def __init__(self, session: Session):
        self.session = session

    def handle_showing_added(self, event: events.ShowingAdded):
        showing_id = str(event.entity_id)
        if self.session.query(ShowingDetail).filter_by(showing_id=showing_id).first():
            msg = f"Showing {showing_id} already exists"
            raise ValueError(msg)
        all_seats = event.available_seats
        row = ShowingDetail(
            showing_id=showing_id,
            movie_name=event.movie_name,
            poster_url=event.movie_poster,
            duration=event.duration,
            start_time=event.start_time,
            available_seats=ShowingDetail.seats_to_str(all_seats),
            reserved_seats='',
            all_seats=ShowingDetail.seats_to_str(all_seats),
        )
        self.session.add(row)
        self.session.commit()

    def handle_ticket_reserved(self, event: events.TicketReserved):
        showing_id = str(event.showing_id)
        row = self.session.query(ShowingDetail).filter_by(showing_id=showing_id).first()
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
        self.session.commit()

    def handle_ticket_cancelled(self, event: events.TicketCancelled):
        showing_id = str(event.showing_id)
        row = self.session.query(ShowingDetail).filter_by(showing_id=showing_id).first()
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
        self.session.commit()

    def get_registry(self):
        # Returns a dict mapping event predicates to handler functions

        return {
            lambda e: isinstance(e, events.ShowingAdded): self.handle_showing_added,
            lambda e: isinstance(e, events.TicketReserved): self.handle_ticket_reserved,
            lambda e: isinstance(e, events.TicketCancelled): self.handle_ticket_cancelled,
        }


# Helper to register with the event bus


def register_showing_detail_projector(event_bus, session):
    projector = ShowingDetailProjector(session)
    registry = projector.get_registry()
    for predicate, handler in registry.items():
        event_bus.subscribe(predicate, handler)
    return projector
