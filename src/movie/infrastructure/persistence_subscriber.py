from contextlib import contextmanager

from .event import DomainEvent
from .store import IEventStore, StreamEvent


class PersistenceSubscriber:
    def __init__(self, event_store: 'IEventStore'):
        self._event_store = event_store

    def store_event(self, event: DomainEvent):
        conditioned = StreamEvent(stream_id=event.entity_id, version=event.entity_version, event=event)
        self._event_store.save(conditioned)

    @contextmanager
    def listen(self):
        yield self._event_store
