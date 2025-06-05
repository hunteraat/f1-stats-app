from flask import jsonify, request

from services import session_service
from . import sessions_bp


@sessions_bp.route("/", methods=["GET"])
def get_sessions():
    """Returns a list of all sessions, optionally filtered by year."""
    try:
        year = request.args.get("year", type=int)
        sessions = session_service.get_all_sessions(year)
        return jsonify(sessions)
    except Exception:
        return jsonify({"error": "An internal error occurred"}), 500


@sessions_bp.route("/<int:session_id>/positions", methods=["GET"])
def get_session_positions(session_id):
    """Get position data for a specific session."""
    try:
        position_data = session_service.get_session_positions(session_id)
        if not position_data:
            return jsonify({"error": "Session not found"}), 404
        return jsonify(position_data)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An internal error occurred"}), 500
