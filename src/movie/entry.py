import atexit
import uuid

from flask import Flask
from sqlalchemy import Connection, Engine, create_engine, select, text
from sqlalchemy.orm import Session

from . import services
from .infrastructure.store import Base, IEventStore, SavedEvent, StreamEvent
from .slices import add_movie


class SqlAlchemyEventStore(IEventStore):
    def __init__(self, engine: Engine):
        self._engine = engine

    def load_stream(self, stream_id: str):
        stream_id_ = stream_id.replace("-", "")
        stream_uuid = uuid.UUID(stream_id_)
        stmt = select(SavedEvent).where(SavedEvent.stream_id == stream_uuid)
        with Session(self._engine) as session:
            results = session.scalars(stmt).all()
        return [event.to_domain_event() for event in results]

    def save(self, *events: StreamEvent):
        with Session(self._engine) as session:
            session.add_all([e.to_store() for e in events])
            session.commit()


def create_app():
    app = Flask(__name__)
    app = services.init_app(app)
    engine = create_engine('sqlite:///movie.db')

    def connection_factory():
        with engine.connect() as conn:
            yield conn

    Base.metadata.create_all(engine)

    ping = text('SELECT 1')
    services.register_factory(
        app, Connection, connection_factory, ping=lambda conn: conn.execute(ping), on_registry_close=engine.dispose
    )

    def event_store_factory():
        return SqlAlchemyEventStore(engine)

    services.register_factory(app, IEventStore, event_store_factory)

    @atexit.register
    def cleanup() -> None:
        services.close_registry(app)

    app.register_blueprint(add_movie.bp)
    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True, port=5001)
