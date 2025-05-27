from flask import jsonify, request
from sqlalchemy import func
from extensions import db
from models import Session, DriverSession, Position, Lap
from utils import add_cors_headers
from . import sessions_bp

sessions_bp = add_cors_headers(sessions_bp)

@sessions_bp.route('/', methods=['GET'])
def get_sessions():
    year = request.args.get('year', type=int)
    
    query = Session.query
    if year:
        query = query.filter(Session.year == year)
    
    sessions = query.order_by(Session.date_start.desc()).all()
    
    return jsonify([{
        'id': session.id,
        'session_key': session.session_key,
        'session_name': session.session_name,
        'date_start': session.date_start.isoformat() if session.date_start else None,
        'location': session.location,
        'country_name': session.country_name,
        'circuit_short_name': session.circuit_short_name,
        'year': session.year,
        'session_type': session.session_type,
        'driver_count': len(session.driver_sessions)
    } for session in sessions])

@sessions_bp.route('/<int:session_id>/positions', methods=['GET'])
def get_session_positions(session_id):
    """Get position data for a specific session"""
    driver_session = DriverSession.query.get_or_404(session_id)
    positions = Position.query.filter_by(driver_session_id=session_id).order_by(Position.date).all()
    
    return jsonify({
        'driver_session': {
            'driver_name': driver_session.driver.full_name,
            'session_name': driver_session.session.session_name,
            'final_position': driver_session.final_position
        },
        'positions': [{
            'date': pos.date.isoformat(),
            'position': pos.position
        } for pos in positions]
    }) 