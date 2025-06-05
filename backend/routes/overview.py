from flask import jsonify, request
from models import db, Driver, Session, DriverSession
from utils import add_cors_headers
from . import overview_bp

overview_bp = add_cors_headers(overview_bp)


@overview_bp.route("/", methods=["GET"])
def get_stats_summary():
    try:
        year = request.args.get("year", type=int)

        if year:
            drivers_q = db.session.query(Driver)
            drivers_q = drivers_q.join(DriverSession).join(Session)
            drivers_q = drivers_q.filter(Session.year == year, Driver.is_active)
            total_drivers = drivers_q.distinct().count()

            total_sessions = Session.query.filter(Session.year == year).count()

            sessions_q = Session.query.filter(Session.year == year)
            latest_session = sessions_q.order_by(Session.date_start.desc()).first()
        else:
            total_drivers = Driver.query.count()
            total_sessions = Session.query.count()
            latest_session = Session.query.order_by(Session.date_start.desc()).first()

        active_drivers_q = db.session.query(Driver).join(DriverSession)
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

        return jsonify(
            {
                "total_drivers": total_drivers,
                "active_drivers": active_drivers,
                "total_sessions": total_sessions,
                "latest_session": latest_session_data,
                "year": year,
            }
        )
    except Exception as e:
        return jsonify({"error": str(e)}), 500
