from datetime import datetime
from uuid import UUID

from pydantic import Field

from movie.infrastructure.event import DomainEvent


class MovieAdded(DomainEvent):
    movie_name: str
    movie_poster: str
    duration: int
    event_name: str = Field('MovieAdded', frozen=True)


class ShowingAdded(DomainEvent):
    movie_id: UUID
    start_time: datetime
    available_seats: list[str]
    event_name: str = Field('ShowingAdded', frozen=True)


class TicketReserved(DomainEvent):
    ticket_id: UUID
    user_id: UUID
    seat_id: str
    event_name: str = Field('TicketReserved', frozen=True)

    @property
    def showing_id(self):
        return self.entity_id


class TicketScanned(DomainEvent):
    ticket_id: UUID
    event_name: str = Field('TicketScanned', frozen=True)

    @property
    def showing_id(self):
        return self.entity_id
