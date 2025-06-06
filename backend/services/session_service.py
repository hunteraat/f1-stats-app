from extensions import db
from models import Session, DriverSession, Position


def get_all_sessions(year=None):
    """
    Retrieves a list of all sessions, optionally filtered by year.
    """
    query = Session.query
    if year:
        query = query.filter(Session.year == year)

    sessions = query.order_by(Session.date_start.desc()).all()
    return [s.to_dict() for s in sessions]


def get_session_positions(session_id):
    """
    Retrieves position data for a specific session.
    """
    if not session_id:
        raise ValueError("session_id parameter is required")

    driver_session = db.session.get(DriverSession, session_id)
    if not driver_session:
        return None

    positions = (
        Position.query.filter_by(driver_session_id=session_id)
        .order_by(Position.date)
        .all()
    )

    return {
        "driver_session": driver_session.to_dict(),
        "positions": [p.to_dict() for p in positions],
    }
