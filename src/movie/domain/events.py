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


class TicketCancelled:
    pass


class TicketReserved:
    pass
