import flask
from sqlalchemy.orm import Session

from movie import services
from movie.slices.showing_detail.model import ShowingDetail

bp = flask.Blueprint('detail_showing_view', __name__)


@bp.get('/showing/<string:showing_id>')
def showing_detail(showing_id):
    session = services.get(Session)
    showing = session.query(ShowingDetail).filter_by(showing_id=showing_id).one_or_none()
    return flask.render_template('showing_detail.html', showing=showing)
