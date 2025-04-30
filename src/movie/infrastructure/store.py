import abc
from datetime import datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

from movie.infrastructure.event import DomainEvent, utc_now

event_to_class_map = {
    # 'EventName': EventClass,
}


class Event(BaseModel):
    model_config = ConfigDict(extra='forbid', frozen=True)


class StreamEvent(BaseModel):
    """Represents on bundle in a stream of bundles for one item."""

    stream_id: str
    version: int
    event: DomainEvent

    def to_store(self) -> 'SavedEvent':
        return SavedEvent(
            stream_id=self.stream_id,
            stream_version=self.version,
            event_name=self.event.event_name,
            event_data=self.event.model_dump(),
            meta_data={},
            stored_at=utc_now(),
        )


class SavedEvent(BaseModel):
    id: int = Field(default_factory=uuid4)
    stream_id: str
    stream_version: int
    event_name: str
    event_data: dict
    meta_data: dict
    stored_at: datetime = Field(default_factory=utc_now)

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
    def save(self, *stream_event: StreamEvent):
        raise NotImplementedError

    @abc.abstractmethod
    def load_stream(self, stream_id):
        raise NotImplementedError
