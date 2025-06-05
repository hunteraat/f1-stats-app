from flask import jsonify
from services import year_service
from . import years_bp


@years_bp.route("/", methods=["GET"])
def get_available_years():
    """Get list of years with sync status"""
    try:
        years_data = year_service.get_available_years_with_details()
        return jsonify(years_data)
    except Exception:
        return jsonify({"error": "An internal error occurred"}), 500
