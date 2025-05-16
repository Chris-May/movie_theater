from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String
from sqlalchemy.orm import Session

from movie import services
from movie.domain import events
from movie.infrastructure.store import Base, SavedEvent

TICKET_THRESHOLD_FOR_ENTRY = 5


class UserTicketCount(Base):
    __tablename__ = 'user_ticket_count'
    user_id = Column(String, primary_key=True)
    month = Column(DateTime, primary_key=True)  # First day of the month
    ticket_count = Column(Integer, nullable=False, default=0)
    last_updated = Column(DateTime, nullable=False)

    def __repr__(self):
        return (
            '<UserTicketCount '
            f'user_id={self.user_id}, '
            f'month={self.month}, '
            f'ticket_count={self.ticket_count}, '
            f'last_updated={self.last_updated} '
            '>'
        )


async def handle_ticket_scan(event: events.TicketScanned):
    session = services.get(Session)
    await scan_ticket(event, session)


async def scan_ticket(event, session):
    events = [
        e.to_domain_event()
        for e in (
            session.query(SavedEvent)
            .where(SavedEvent.stream_id == event.showing_id, SavedEvent.event_name == 'TicketReserved')
            .all()
        )
    ]
    matching_event = next(e for e in events if e.ticket_id == event.ticket_id)

    user_id = str(matching_event.user_id)
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # noqa: DTZ005
    # Get or create a user record for this month
    user_count = session.query(UserTicketCount).filter_by(user_id=user_id, month=current_month).first()
    if not user_count:
        user_count = UserTicketCount(user_id=user_id, month=current_month, ticket_count=0, last_updated=datetime.now())  # noqa: DTZ005
        session.add(user_count)
    # Increment the count
    user_count.ticket_count += 1
    user_count.last_updated = datetime.now()  # noqa: DTZ005
    session.commit()


async def get_eligible_users():
    """Returns a list of users who have reserved at least 5 tickets this month"""
    session = services.get(Session)
    current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)  # noqa: DTZ005

    return (
        session.query(UserTicketCount)
        .filter(UserTicketCount.ticket_count >= TICKET_THRESHOLD_FOR_ENTRY, UserTicketCount.month == current_month)
        .all()
    )
