import flask

from movie.slices.giveaway.model import get_eligible_users

bp = flask.Blueprint('giveaway_view', __name__)


@bp.get('/giveaway/eligible')
def eligible_users():
    users = get_eligible_users()
    return flask.render_template('giveaway/eligible.html', users=users)
