from uuid import UUID

import quart
from quart import request

from movie.domain.repos import ShowingRepo

bp = quart.Blueprint("scan_ticket", __name__)


@bp.post('/ticket/<string:ticket_id>/scan')
async def scan_ticket(ticket_id: str):
    """
    Scan a ticket by its ID.
    This endpoint is called when a ticket is scanned at the theater entrance.
    """
    # Get the showing ID from the form data
    form = await request.form
    showing_id = form.get('showing_id')

    if not showing_id:
        return quart.jsonify({"error": "Showing ID is required"}), 400

    # Get the showing
    showing = await ShowingRepo().get_showing(UUID(showing_id))

    # Scan the ticket
    await showing.scan_ticket(UUID(ticket_id))

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
