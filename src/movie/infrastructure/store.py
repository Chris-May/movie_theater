import abc
from datetime import datetime
from uuid import UUID, uuid4

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import JSON, Uuid
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from movie.domain import events
from movie.infrastructure.event import DomainEvent, utc_now

event_to_class_map = {
    'MovieAdded': events.MovieAdded,
    'ShowingAdded': events.ShowingAdded,
    'TicketReserved': events.TicketReserved,
}


class Event(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)


class StreamEvent(BaseModel):
    """Represents on bundle in a stream of bundles for one item."""

    stream_id: UUID
    version: int
    event: DomainEvent

    def to_store(self) -> 'SavedEvent':
        return SavedEvent(
            stream_id=self.stream_id,
            stream_version=self.version,
            event_name=self.event.event_name,
            event_data=self.event.model_dump_json(),
            meta_data={},
            stored_at=utc_now(),
        )


class Base(DeclarativeBase): ...


class SavedEvent(Base):
    __tablename__ = 'events'
    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4, type_=Uuid)
    stream_id: Mapped[UUID] = mapped_column(index=True, type_=Uuid)
    stream_version: Mapped[int]
    event_name: Mapped[str]
    event_data: Mapped[str] = mapped_column(JSON)
    meta_data: Mapped[str] = mapped_column(JSON)
    stored_at: Mapped[datetime] = Field(default_factory=utc_now)

    def to_domain_event(self):
        klass = event_to_class_map[self.event_name]
        return klass.deserialize(self.event_data)


class ConcurrentStreamWriteError(Exception):
    def __init__(self, stream_id, version):
        self.stream_id = stream_id
        self.version = version
        self.message = f'Version {version} already exists for stream {stream_id}'


class IEventStore(abc.ABC):
    @abc.abstractmethod
    def save(self, *stream_event: StreamEvent | DomainEvent):
        raise NotImplementedError

    @abc.abstractmethod
    def load_stream(self, stream_id):
        raise NotImplementedError
