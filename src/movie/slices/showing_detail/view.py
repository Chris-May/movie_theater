import flask
from sqlalchemy.orm import Session

from movie import services
from movie.domain.model import UserID
from movie.slices.showing_detail.model import ShowingDetail

bp = flask.Blueprint('detail_showing_view', __name__)


@bp.get('/showing/<string:showing_id>')
def showing_detail(showing_id):
    session = services.get(Session)
    showing = session.query(ShowingDetail).filter_by(showing_id=showing_id).one_or_none()
    user_id = services.get(UserID)
    return flask.render_template('showing_detail.html', showing=showing, user_id=user_id)
