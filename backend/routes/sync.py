from flask import jsonify
from . import sync_bp
from services.sync_service import run_sync_for_year
from models import YearData, db, Lap, Session, DriverSession


@sync_bp.route("/data/<int:year>", methods=["POST"])
async def sync_f1_data_route(year):
    """
    Route to trigger the F1 data synchronization for a given year.
    """
    try:
        result = await run_sync_for_year(year)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@sync_bp.route("/status/<int:year>", methods=["GET"])
def get_sync_status(year):
    """Get the current sync status for a year"""
    year_data = YearData.query.filter_by(year=year).first()
    if not year_data:
        return jsonify(
            {
                "status": "not_started",
                "progress": 0,
                "message": "No sync data available",
            }
        )
    return jsonify(year_data.to_dict())


@sync_bp.route("/database/reset", methods=["POST"])
def reset_database():
    """
    Endpoint to reset the database. Use with caution.
    """
    try:
        db.drop_all()
        db.create_all()
        return jsonify({"success": True, "message": "Database reset successfully."})
    except Exception as e:
        return jsonify({"error": f"Failed to reset database: {e}"}), 500


@sync_bp.route("/data/<int:year>/clear-laps", methods=["POST"])
def clear_lap_data(year):
    """Clear all lap data for a specific year"""
    try:
        sessions = Session.query.filter_by(year=year).all()
        session_ids = [s.id for s in sessions]

        driver_sessions_q = DriverSession.query.filter(
            DriverSession.session_id.in_(session_ids)
        )
        driver_session_ids = [ds.id for ds in driver_sessions_q.all()]

        deleted_count = Lap.query.filter(
            Lap.driver_session_id.in_(driver_session_ids)
        ).delete(synchronize_session="fetch")

        db.session.commit()

        year_data = YearData.query.filter_by(year=year).first()
        if year_data:
            year_data.last_incremental_sync = None
            db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": (
                    f"Successfully deleted {deleted_count} " f"lap records for {year}"
                ),
            }
        )
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to clear lap data: {e}"}), 500
