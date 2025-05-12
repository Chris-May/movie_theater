from functools import singledispatchmethod
from typing import TYPE_CHECKING

from .event import DomainEvent, DomainEventCollection
from .exceptions import UnknownEventError

if TYPE_CHECKING:
    from uuid import UUID


class Entity:
    def __init__(self, *events):
        self.register_events()
        self._pending_events = []
        self.version = 0
        self.id: UUID
        for event in events:
            self.apply(event)

    def increment_version(self):
        self.version += 1

    async def publish(self, event: DomainEvent):
        from .pubsub import publish

        self.apply(event)
        await publish(event)

    @singledispatchmethod
    def apply(self, event):
        raise UnknownEventError(event)

    def register_events(self):
        raise NotImplementedError

    @classmethod
    def build_from_event_collection(cls, event_collection: DomainEventCollection):
        entity = cls()
        for event in event_collection:
            entity.apply(event)
        return entity
