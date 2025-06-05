from flask import jsonify, request

from models import Session, DriverSession, Position
from . import sessions_bp


@sessions_bp.route("/", methods=["GET"])
def get_sessions():
    """Returns a list of all sessions, optionally filtered by year."""
    year = request.args.get("year", type=int)

    query = Session.query
    if year:
        query = query.filter(Session.year == year)

    sessions = query.order_by(Session.date_start.desc()).all()
    return jsonify([s.to_dict() for s in sessions])


@sessions_bp.route("/<int:session_id>/positions", methods=["GET"])
def get_session_positions(session_id):
    """Get position data for a specific session."""
    driver_session = DriverSession.query.get_or_404(session_id)
    positions = (
        Position.query.filter_by(driver_session_id=session_id)
        .order_by(Position.date)
        .all()
    )

    return jsonify(
        {
            "driver_session": driver_session.to_dict(),
            "positions": [p.to_dict() for p in positions],
        }
    )
