from models import db, Driver, Session, DriverSession


def get_stats_summary(year=None):
    """
    Calculates a summary of statistics, optionally filtered by year.
    """
    if year:
        drivers_q = (
            db.session.query(Driver.id)
            .join(DriverSession)
            .join(Session)
            .filter(Session.year == year, Driver.is_active)
        )
        total_drivers = drivers_q.distinct().count()

        total_sessions = Session.query.filter(Session.year == year).count()

        sessions_q = Session.query.filter(Session.year == year)
        latest_session = sessions_q.order_by(Session.date_start.desc()).first()

    else:
        total_drivers = Driver.query.count()
        total_sessions = Session.query.count()
        latest_session = Session.query.order_by(Session.date_start.desc()).first()

    active_drivers_q = db.session.query(Driver.id).join(DriverSession)
    active_drivers_count = active_drivers_q.distinct().count()
    active_drivers = total_drivers if year else active_drivers_count

    latest_session_data = None
    if latest_session:
        date_start = latest_session.date_start
        latest_session_data = {
            "name": latest_session.session_name,
            "location": latest_session.location,
            "date": date_start.isoformat() if date_start else None,
        }

    return {
        "total_drivers": total_drivers,
        "active_drivers": active_drivers,
        "total_sessions": total_sessions,
        "latest_session": latest_session_data,
        "year": year,
    }
