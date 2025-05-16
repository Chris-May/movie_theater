import json
from uuid import UUID

import quart
from quart import request
from sqlalchemy.orm import Session

from movie import services
from movie.domain.repos import ShowingRepo
from movie.infrastructure.store import SavedEvent
from movie.slices.scan_ticket.model import get_scanned_tickets

bp = quart.Blueprint("scan_ticket", __name__)


@bp.post('/ticket/scan')
async def scan_ticket():
    """
    This endpoint is called when a ticket is scanned at the theater entrance.
    """
    # Get the showing ID from the form data
    form = await request.form
    showing_id = form.get('showing_id')
    seat = form.get('seat')
    session = services.get(Session)
    events = session.query(SavedEvent).filter_by(stream_id=UUID(showing_id), event_name='TicketReserved').all()
    matching_event = next(e for e in events if json.loads(e.event_data)['seat_id'] == seat)
    showing = await ShowingRepo().get_showing(UUID(showing_id))
    ticket_id = json.loads(matching_event.event_data)['ticket_id']
    await showing.scan_ticket(ticket_id)

    return quart.jsonify(
        {
            "success": True,
            "message": f"Ticket {ticket_id} scanned successfully",
            "ticket_id": ticket_id,
            "showing_id": showing_id,
        }
    )


@bp.get('/scan')
async def scan_ticket_form():
    """
    Render a form for scanning tickets.
    This is a simple UI for testing the ticket scanning functionality.
    """
    return await quart.render_template('scan_ticket.html')


@bp.get('/scanned_tickets')
async def show_scanned_tickets():
    """
    Get a list of scanned tickets.
    """
    return await get_scanned_tickets()
