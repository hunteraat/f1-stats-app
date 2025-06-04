from flask import Blueprint, jsonify, request
from extensions import db
from models import DriverStats, DriverSessionStats
from utils import add_cors_headers
from . import drivers_bp

drivers_bp = add_cors_headers(drivers_bp)

@drivers_bp.route('/', methods=['GET'])
def get_drivers():
    year = request.args.get('year', type=int)
    
    if not year:
        return jsonify({'error': 'Year parameter is required'}), 400
    
    drivers = DriverStats.query.filter_by(year=year).order_by(DriverStats.position).all()
    
    drivers_data = [{
        'driver_number': d.driver_number,
        'full_name': d.full_name,
        'team_name': d.team_name,
        'team_colour': d.team_colour,
        'country_code': d.country_code,
        'headshot_url': d.headshot_url,
        'position': d.position,
        'podiums': d.podiums,
        'wins': d.wins,
        'races': d.races,
        'fastest_laps': d.fastest_laps,
        'points': d.points,
        'average_position': d.average_position,
        'is_active': d.is_active,
        'year': d.year
    } for d in drivers]
    
    return jsonify(drivers_data)

@drivers_bp.route('/<int:driver_number>', methods=['GET'])
def get_driver(driver_number):
    year = request.args.get('year', type=int)
    
    if not year:
        return jsonify({'error': 'Year parameter is required'}), 400
    
    driver = DriverStats.query.filter_by(driver_number=driver_number, year=year).first_or_404()
    
    driver_data = {
        'driver_number': driver.driver_number,
        'full_name': driver.full_name,
        'team_name': driver.team_name,
        'races': driver.races,
        'country_code': driver.country_code,
        'headshot_url': driver.headshot_url,
        'position': driver.position,
        'podiums': driver.podiums,
        'wins': driver.wins,
        'fastest_laps': driver.fastest_laps,
        'points': driver.points,
        'average_position': driver.average_position,
        'is_active': driver.is_active,
        'year': driver.year
    }
    
    return jsonify(driver_data)

@drivers_bp.route('/<int:driver_number>/sessions', methods=['GET'])
def get_driver_sessions(driver_number):
    year = request.args.get('year', type=int)
    
    if not year:
        return jsonify({'error': 'Year parameter is required'}), 400
    
    sessions = DriverSessionStats.query.filter_by(
        driver_number=driver_number,
        year=year
    ).order_by(DriverSessionStats.date_start.desc()).all()
    
    sessions_data = [{
        'driver_number': s.driver_number,
        'full_name': s.full_name,
        'team_name': s.team_name,
        'session_name': s.session_name,
        'session_type': s.session_type,
        'location': s.location,
        'date_start': s.date_start.isoformat() if s.date_start else None,
        'final_position': s.final_position,
        'fastest_lap': s.fastest_lap,
        'points': s.points,
        'year': s.year
    } for s in sessions]
    
    return jsonify(sessions_data) 