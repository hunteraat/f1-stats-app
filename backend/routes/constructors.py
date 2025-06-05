from flask import jsonify, request
from . import constructors_bp
from services import constructor_service


@constructors_bp.route("/", methods=["GET"])
def get_constructors():
    """
    Returns a list of constructors for a given year, ordered by position.
    If a team_name is provided, returns the data for that specific constructor.
    """
    try:
        year = request.args.get("year", type=int)
        team_name = request.args.get("team_name", type=str)
        constructors = constructor_service.get_constructors_by_year(year, team_name)
        if not constructors:
            return jsonify({"error": "No data found for the given criteria"}), 404
        return jsonify(constructors)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An internal error occurred"}), 500


@constructors_bp.route("/<string:team_name>", methods=["GET"])
def get_constructor(team_name):
    """Returns data for a specific constructor."""
    try:
        year = request.args.get("year", type=int)
        constructor = constructor_service.get_constructor_details(year, team_name)
        if not constructor:
            return jsonify({"error": "Constructor not found"}), 404
        return jsonify(constructor)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An internal error occurred"}), 500


@constructors_bp.route("/<int:year>", methods=["GET"])
def get_constructor_standings(year):
    """
    Returns the constructor standings for a given year.
    """
    try:
        standings = constructor_service.get_constructor_standings_by_year(year)
        if not standings:
            return jsonify({"error": "No standings found for this year"}), 404
        return jsonify(standings)
    except ValueError as e:
        return jsonify({"error": str(e)}), 400
    except Exception:
        return jsonify({"error": "An internal error occurred"}), 500
