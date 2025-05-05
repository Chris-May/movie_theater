import flask

bp = flask.Blueprint('detail_showing_view', __name__)


@bp.get('/showing/<string:showing_id>')
def showing_detail(showing_id):  # noqa: ARG001
    return flask.render_template('showing_detail.html')
