import asyncio

from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from tqdm import tqdm

from movie.infrastructure.store import Base, SavedEvent
from movie.slices.giveaway.model import scan_ticket


async def main():
    engine = create_engine('sqlite:///movies.db')
    Base.metadata.create_all(engine)
    with Session(engine) as session:
        scanned_tickets = [
            evt.to_domain_event()
            for evt in session.query(SavedEvent).filter(SavedEvent.event_name == 'TicketScanned').all()
        ]

        for event in tqdm(scanned_tickets):
            await scan_ticket(event, session)


def go():
    asyncio.run(main())


if __name__ == "__main__":
    asyncio.run(main())
