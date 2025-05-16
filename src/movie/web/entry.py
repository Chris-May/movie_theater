import atexit
import tomllib
import uuid
from pathlib import Path

import quart_flask_patch  # noqa: F401
from jinja2 import FileSystemLoader
from quart import Quart
from sqlalchemy import Engine, create_engine, select
from sqlalchemy.orm import Session

import movie.slices.reserve_ticket.view
import movie.slices.scan_ticket.view
from movie import services
from movie.domain.model import UserID
from movie.infrastructure.event import DomainEvent
from movie.infrastructure.store import Base, IEventStore, SavedEvent, StreamEvent
from movie.slices import add_movie, add_showing
from movie.slices.giveaway import view as giveaway_view
from movie.slices.showing_detail import view
from movie.slices.view_now_playing import view as view_now_playing


class SqlAlchemyEventStore(IEventStore):
    def __init__(self, engine: Engine):
        self._engine = engine

    def load_stream(self, stream_id: str | uuid.UUID):
        stream_id_ = str(stream_id).replace("-", "")
        stream_uuid = uuid.UUID(stream_id_)
        stmt = select(SavedEvent).where(SavedEvent.stream_id == stream_uuid)
        with Session(self._engine) as session:
            results = session.scalars(stmt).all()
        return [event.to_domain_event() for event in results]

    async def save(self, *events: StreamEvent | DomainEvent):
        ensured_events = [
            e if isinstance(e, StreamEvent) else StreamEvent(stream_id=e.entity_id, version=e.entity_version, event=e)
            for e in events
        ]
        with Session(self._engine) as session:
            session.add_all([e.to_store() for e in ensured_events])
            session.commit()


def create_app(config_file=None) -> Quart:
    app = Quart(__name__)
    app.config.from_object('movie.default_settings')
    if config_file:
        app.config.from_file(config_file, load=tomllib.load, text=False)
    app = services.init_app(app)
    app.jinja_options = dict(loader=FileSystemLoader(searchpath=list(Path(__file__).parents[1].rglob('templates'))))
    app.static_folder = Path(__file__).parent / 'static'
    app.static_url_path = '/static'
    engine = create_engine(app.config['DATABASE_CONNECTION'])

    def session_factory():
        with Session(engine) as session:
            yield session

    services.register_factory(app, Session, session_factory)
    services.register_value(app, UserID, uuid.UUID('00000000-0000-4000-8000-000000000000'))

    def event_store_factory():
        return SqlAlchemyEventStore(engine)

    services.register_factory(app, IEventStore, event_store_factory)

    @atexit.register
    def cleanup() -> None:
        services.close_registry(app)

    app.register_blueprint(add_movie.bp)
    app.register_blueprint(add_showing.bp)
    app.register_blueprint(view.bp)
    app.register_blueprint(movie.slices.reserve_ticket.view.bp)
    app.register_blueprint(movie.slices.scan_ticket.view.bp)
    app.register_blueprint(view_now_playing.bp)
    app.register_blueprint(giveaway_view.bp)
    Base.metadata.create_all(engine)

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(debug=True, port=5001)
