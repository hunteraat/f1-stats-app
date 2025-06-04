from flask import Blueprint, jsonify, request
from extensions import db
from models import ConstructorStats
from utils import add_cors_headers
from . import constructors_bp

constructors_bp = add_cors_headers(constructors_bp)

@constructors_bp.route('/', methods=['GET'])
def get_constructors():
    year = request.args.get('year', type=int)
    
    if not year:
        return jsonify({'error': 'Year parameter is required'}), 400
    
    constructors = ConstructorStats.query.filter_by(year=year).order_by(ConstructorStats.position).all()
    
    constructors_data = [{
        'team_name': c.team_name,
        'team_colour': c.team_colour,
        'position': c.position,
        'points': c.points,
        'podiums': c.podiums,
        'wins': c.wins,
        'fastest_laps': c.fastest_laps,
        'races': c.races,
        'year': c.year
    } for c in constructors]
    
    return jsonify(constructors_data)

@constructors_bp.route('/<string:team_name>', methods=['GET'])
def get_constructor(team_name):
    year = request.args.get('year', type=int)
    
    if not year:
        return jsonify({'error': 'Year parameter is required'}), 400
    
    constructor = ConstructorStats.query.filter_by(team_name=team_name, year=year).first_or_404()
    
    constructor_data = {
        'team_name': constructor.team_name,
        'team_colour': constructor.team_colour,
        'position': constructor.position,
        'points': constructor.points,
        'podiums': constructor.podiums,
        'wins': constructor.wins,
        'fastest_laps': constructor.fastest_laps,
        'races': constructor.races,
        'year': constructor.year
    }
    
    return jsonify(constructor_data) 