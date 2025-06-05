from flask import Blueprint, jsonify, request
from extensions import db
from models import DriverStats, DriverSessionStats, Driver
from utils import add_cors_headers
from . import drivers_bp

drivers_bp = add_cors_headers(drivers_bp)


@drivers_bp.route("/", methods=["GET"])
def get_drivers():
    """
    Returns driver statistics.
    Can be filtered by year and driver_number.
    """
    year = request.args.get("year", type=int)
    driver_number = request.args.get("driver_number", type=int)

    if not year:
        return jsonify({"error": "Year parameter is required"}), 400

    query = DriverStats.query.filter_by(year=year)

    if driver_number:
        query = query.filter_by(driver_number=driver_number)

    drivers = query.order_by(DriverStats.position).all()

    if not drivers:
        return jsonify({"error": "No drivers found for the given criteria"}), 404

    return jsonify([d.to_dict() for d in drivers])


@drivers_bp.route("/sessions", methods=["GET"])
def get_driver_sessions():
    """
    Returns session statistics for a given driver and year.
    """
    year = request.args.get("year", type=int)
    driver_number = request.args.get("driver_number", type=int)

    if not year or not driver_number:
        return (
            jsonify({"error": "Year and driver_number parameters are required"}),
            400,
        )

    sessions = (
        DriverSessionStats.query.filter_by(driver_number=driver_number, year=year)
        .order_by(DriverSessionStats.date_start.desc())
        .all()
    )

    if not sessions:
        return (
            jsonify({"error": "No session data found for the given criteria"}),
            404,
        )

    return jsonify([s.to_dict() for s in sessions])
