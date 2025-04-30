from movie.infrastructure.event import DomainEvent


class EventSourcingError(Exception):
    def __init__(self, message: str):
        self.message = message


class UnknownEventError(EventSourcingError):
    def __init__(self, event: DomainEvent):
        self.message = f"Unknown event: {event}"
