from flask import Blueprint, jsonify, request
from models import db, Driver, Session, DriverSession
from utils import add_cors_headers
from . import overview_bp

overview_bp = add_cors_headers(overview_bp)

@overview_bp.route('/', methods=['GET'])
def get_stats_summary():
    try:
        year = request.args.get('year', type=int)
        
        if year:
            total_drivers = db.session.query(Driver).join(DriverSession).join(Session).filter(Session.year == year, Driver.is_active == True).distinct().count()
            total_sessions = Session.query.filter(Session.year == year).count()
            latest_session = Session.query.filter(Session.year == year).order_by(Session.date_start.desc()).first()
        else:
            total_drivers = Driver.query.count()
            total_sessions = Session.query.count()
            latest_session = Session.query.order_by(Session.date_start.desc()).first()
        
        active_drivers = total_drivers if year else db.session.query(Driver).join(DriverSession).distinct().count()
        
        return jsonify({
            'total_drivers': total_drivers,
            'active_drivers': active_drivers,
            'total_sessions': total_sessions,
            'latest_session': {
                'name': latest_session.session_name if latest_session else None,
                'location': latest_session.location if latest_session else None,
                'date': latest_session.date_start.isoformat() if latest_session and latest_session.date_start else None
            } if latest_session else None,
            'year': year
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500 