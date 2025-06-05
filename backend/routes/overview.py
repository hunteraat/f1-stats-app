from flask import jsonify, request
from services import overview_service
from utils import add_cors_headers
from . import overview_bp

overview_bp = add_cors_headers(overview_bp)


@overview_bp.route("/", methods=["GET"])
def get_stats_summary():
    """
    Returns a summary of driver and session statistics.
    Can be filtered by year.
    """
    try:
        year = request.args.get("year", type=int)
        summary_data = overview_service.get_stats_summary(year)
        return jsonify(summary_data)
    except Exception:
        # Using a generic error message for any exception
        return jsonify({"error": "An internal error occurred"}), 500
