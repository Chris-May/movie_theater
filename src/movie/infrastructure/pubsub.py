import inspect
import logging
from collections import defaultdict
from collections.abc import Callable

from movie import services
from movie.domain import events
from movie.infrastructure.event import DomainEvent
from movie.infrastructure.store import IEventStore, StreamEvent
from movie.slices import now_playing
from movie.slices.giveaway import model as giveaway_model
from movie.slices.scan_ticket import model as scan_ticket_model
from movie.slices.showing_detail import model as showing_detail_model

logger = logging.getLogger(__name__)

_event_handlers: dict[Callable, list[Callable]] = defaultdict(list)

_subscriptions = {
    lambda e: isinstance(e, events.ShowingAdded): showing_detail_model.handle_showing_added,
    lambda e: isinstance(e, events.TicketReserved): showing_detail_model.handle_ticket_reserved,
    lambda e: isinstance(e, events.TicketReserved): now_playing.on_ticket_reserved,
    lambda e: isinstance(e, events.ShowingAdded): now_playing.on_new_showing,
    lambda e: isinstance(e, events.ShowingAdded): now_playing.on_ticket_reserved,
    lambda e: isinstance(e, events.TicketScanned): scan_ticket_model.handle_ticket_scanned,
    lambda e: isinstance(e, events.TicketReserved): giveaway_model.handle_ticket_scan,
}


async def publish(event: DomainEvent):
    """Publish a domain event to all subscribers.

    The event is first persisted, then sent to all matching subscribers.
    Each subscriber receives the events only once.
    """
    # First persist the event
    try:
        if isinstance(event, DomainEvent):
            event_store = services.get(IEventStore)
            conditioned = StreamEvent(stream_id=event.entity_id, version=event.entity_version, event=event)
            logger.info('saving event %s %s', conditioned.event.event_name, conditioned.stream_id)
            await event_store.save(conditioned)

            # Then notify subscribers
            matching_handlers = []
            for should_handle, handlers in _event_handlers.items():
                if should_handle(event):
                    for handler in handlers:
                        if handler not in matching_handlers:
                            matching_handlers.append(handler)

            for handler in matching_handlers:
                if inspect.iscoroutinefunction(handler):
                    await handler(event)
                else:
                    handler(event)

    except Exception as e:
        logger.info('Event store not available: %s', e)
        raise


def subscribe(event_predicate: Callable, subscriber: Callable):
    """Subscribe to events matching the given predicate, ensuring no duplicates and preserving order."""
    if subscriber not in _event_handlers[event_predicate]:
        _event_handlers[event_predicate].append(subscriber)


def unsubscribe(event_predicate: Callable, subscriber: Callable):
    """Unsubscribe from events matching the given predicate."""
    _event_handlers[event_predicate].remove(subscriber)


def unsubscribe_all(subscriber):
    predicates_for_removal = []
    for event_predicate, event_handlers in _event_handlers.items():
        event_handlers.remove(subscriber)
        if len(event_handlers) == 0:
            predicates_for_removal.append(event_predicate)

    for predicate in predicates_for_removal:
        del _event_handlers[predicate]


for predicate, handler in _subscriptions.items():
    subscribe(predicate, handler)


class EventListeners:
    pass
