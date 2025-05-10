from uuid import UUID

from movie import services
from movie.domain.model import Showing
from movie.infrastructure.store import IEventStore


class ShowingRepo:
    def __init__(self):
        self._store = services.get(IEventStore)

    def get_showing(self, showing_id: UUID) -> Showing:
        events = self._store.load_stream(str(showing_id))
        return Showing(*events)
