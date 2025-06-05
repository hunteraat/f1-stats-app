from flask import jsonify, request

from services import driver_service
from utils import add_cors_headers
from . import drivers_bp

drivers_bp = add_cors_headers(drivers_bp)


@drivers_bp.route("/", methods=["GET"])
def get_drivers():
    """
    Returns driver statistics.
    Can be filtered by year and driver_number.
    """
    try:
        year = request.args.get("year", type=int)
        driver_number = request.args.get("driver_number", type=int)
        drivers = driver_service.get_driver_stats(year, driver_number)

        if not drivers:
            return jsonify({"error": "No drivers found for the given criteria"}), 404

        return jsonify(drivers)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An internal error occurred"}), 500


@drivers_bp.route("/sessions", methods=["GET"])
def get_driver_sessions():
    """
    Returns session statistics for a given driver and year.
    """
    try:
        year = request.args.get("year", type=int)
        driver_number = request.args.get("driver_number", type=int)
        sessions = driver_service.get_driver_session_stats(year, driver_number)

        if not sessions:
            return (
                jsonify({"error": "No session data found for the given criteria"}),
                404,
            )

        return jsonify(sessions)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An internal error occurred"}), 500
