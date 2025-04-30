import importlib
import inspect
import logging
from collections import defaultdict
from collections.abc import Callable
from importlib import resources as import_res

from api import get_container
from api.domain.events import DomainEvent
from api.infrastructure.store import IEventStore, StreamEvent

logger = logging.getLogger(__name__)

_event_handlers: dict[Callable, list[Callable]] = defaultdict(list)


async def publish(event: DomainEvent):
    """Publish a domain event to all subscribers.

    The event is first persisted, then sent to all matching subscribers.
    Each subscriber receives the event only once.
    """
    # First persist the event
    if isinstance(event, DomainEvent):
        container = get_container()
        event_store = await container.aget(IEventStore)
        conditioned = StreamEvent(stream_id=event.entity_id, version=event.entity_version, event=event)
        logger.info('saving event %s %s', conditioned.event.event_name, conditioned.stream_id)
        event_store.save(conditioned)

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


def load_subscribers(base_package: str):
    """Autoload all subscribe.py modules in the given package."""
    logger.info("Loading subscribers from %s", base_package)
    for resource in import_res.contents(base_package):
        with import_res.path(base_package, resource) as fspath:
            if fspath.is_dir():
                for module_path in fspath.rglob('subscribe.py'):
                    *_, api_part = str(module_path).partition('api/')
                    dotted_path = api_part.replace('/', '.').replace('.py', '')
                    module = importlib.import_module(dotted_path)
                    if hasattr(module, "initialize_subscriber"):
                        logger.info("Initializing subscriber %s", module_path)
                        module.initialize_subscriber()
