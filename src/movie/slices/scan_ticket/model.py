from uuid import UUID

from sqlalchemy import Column, Uuid
from sqlalchemy.orm import Mapped, Session, mapped_column

from movie import services
from movie.domain import events
from movie.domain.model import Showing
from movie.infrastructure.store import Base, IEventStore


class ScannedTicket(Base):
    __tablename__ = 'scanned_tickets'
    ticket_id: Mapped[UUID] = mapped_column(primary_key=True)
    showing_id: Mapped[UUID] = Column(Uuid)
    movie_id: Mapped[UUID] = Column(Uuid)
    user_id: Mapped[UUID] = Column(Uuid)

    def __repr__(self):
        return (
            f"<ScannedTicket ticket_id={self.ticket_id}, showing_id={self.showing_id}, movie_id={self.movie_id}"
            f", user_id={self.user_id}>"
        )


async def handle_ticket_scanned(event: events.TicketScanned):
    """
    Handle the TicketScanned event by creating a record in the ScannedTicket table.
    """
    session, event_store = services.get(Session, IEventStore)

    # Get the showing to retrieve the movie_id
    showing_events = event_store.load_stream(event.showing_id)
    showing = Showing(*showing_events)

    # Create a new ScannedTicket record
    scanned_ticket = ScannedTicket(ticket_id=event.ticket_id, showing_id=event.showing_id, movie_id=showing.movie_id)

    # Add and commit to the database
    session.add(scanned_ticket)
    session.commit()


async def get_scanned_tickets():
    session = services.get(Session)
    return session.query(ScannedTicket).all()
