from pydantic import Field

from movie.infrastructure.event import DomainEvent


class MovieAdded(DomainEvent):
    movie_name: str
    movie_poster: str
    duration: int
    event_name: str = Field('MovieAdded', frozen=True)
