import functools
from datetime import UTC, datetime
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field

utc_now = functools.partial(datetime.now, tz=UTC)


class DomainEvent(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)

    event_id: int = Field(default_factory=uuid4)
    entity_id: str
    entity_version: int
    event_name: str
    stored_at: datetime = Field(default_factory=utc_now)
    metadata: dict = Field(default_factory=dict)

    def serialize(self):
        return self.model_dump()

    @classmethod
    def deserialize(cls, data):
        return cls.model_validate(data)


class DomainEventCollection:
    def __init__(self, events: list[DomainEvent]):
        self.events = events

    def __iter__(self):
        return iter(self.events)

    def __repr__(self):
        return f'<DomainEventCollection {len(self.events)} events>'

    def __bool__(self):
        return bool(self.events)

    def __len__(self):
        return len(self.events)
