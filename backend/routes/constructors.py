from flask import jsonify, request

from . import constructors_bp
from models import ConstructorStats


@constructors_bp.route("/", methods=["GET"])
def get_constructors():
    """
    Returns a list of constructors for a given year, ordered by position.
    If a team_name is provided, returns the data for that specific constructor.
    """
    year = request.args.get("year", type=int)
    team_name = request.args.get("team_name", type=str)

    if not year:
        return jsonify({"error": "Year parameter is required"}), 400

    query = ConstructorStats.query.filter_by(year=year)

    if team_name:
        query = query.filter_by(team_name=team_name)

    constructors = query.order_by(ConstructorStats.position).all()

    if not constructors:
        return jsonify({"error": "No data found for the given criteria"}), 404

    return jsonify([c.to_dict() for c in constructors])


@constructors_bp.route("/<string:team_name>", methods=["GET"])
def get_constructor(team_name):
    year = request.args.get("year", type=int)

    if not year:
        return jsonify({"error": "Year parameter is required"}), 400

    constructor = ConstructorStats.query.filter_by(
        team_name=team_name, year=year
    ).first_or_404()

    constructor_data = {
        "team_name": constructor.team_name,
        "team_colour": constructor.team_colour,
        "position": constructor.position,
        "points": constructor.points,
        "podiums": constructor.podiums,
        "wins": constructor.wins,
        "fastest_laps": constructor.fastest_laps,
        "races": constructor.races,
        "year": constructor.year,
    }

    return jsonify(constructor_data)


@constructors_bp.route("/<int:year>", methods=["GET"])
def get_constructor_standings(year):
    """
    Returns the constructor standings for a given year.
    """
    standings = ConstructorStats.query.filter_by(year=year).order_by(
        ConstructorStats.position
    )
    return jsonify([standing.to_dict() for standing in standings])
