import quart

from movie.slices.giveaway.model import get_eligible_users

bp = quart.Blueprint('giveaway_view', __name__)


@bp.get('/giveaway/eligible')
async def eligible_users():
    users = await get_eligible_users()
    return await quart.render_template('eligible.html', users=users)
