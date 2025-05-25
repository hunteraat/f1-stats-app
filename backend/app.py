from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///f1_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Database Models
class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_number = db.Column(db.Integer, unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(50), nullable=True)
    team_colour = db.Column(db.String(7), nullable=True)
    country_code = db.Column(db.String(3), nullable=True)
    headshot_url = db.Column(db.String(255), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationship to sessions
    sessions = db.relationship('DriverSession', back_populates='driver', cascade='all, delete-orphan')

class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.Integer, unique=True, nullable=False)
    session_name = db.Column(db.String(50), nullable=False)
    date_start = db.Column(db.DateTime, nullable=False)
    date_end = db.Column(db.DateTime, nullable=True)
    gmt_offset = db.Column(db.String(10), nullable=True)
    session_type = db.Column(db.String(20), nullable=False)
    meeting_key = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    country_name = db.Column(db.String(50), nullable=True)
    circuit_short_name = db.Column(db.String(50), nullable=True)
    year = db.Column(db.Integer, nullable=False)
    
    # Relationship to driver sessions
    driver_sessions = db.relationship('DriverSession', back_populates='session', cascade='all, delete-orphan')

class DriverSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    position = db.Column(db.Integer, nullable=True)
    points = db.Column(db.Float, nullable=True)
    
    # Relationships
    driver = db.relationship('Driver', back_populates='sessions')
    session = db.relationship('Session', back_populates='driver_sessions')

# OpenF1 API base URL
OPENF1_BASE_URL = "https://api.openf1.org/v1"

@app.route('/')
def home():
    return jsonify({"message": "F1 Statistics API is running!"})

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    drivers = Driver.query.all()
    return jsonify([{
        'id': driver.id,
        'driver_number': driver.driver_number,
        'full_name': driver.full_name,
        'team_name': driver.team_name,
        'team_colour': driver.team_colour,
        'country_code': driver.country_code,
        'headshot_url': driver.headshot_url,
        'last_updated': driver.last_updated.isoformat() if driver.last_updated else None,
        'session_count': len(driver.sessions)
    } for driver in drivers])

@app.route('/api/drivers/<int:driver_id>/sessions', methods=['GET'])
def get_driver_sessions(driver_id):
    driver = Driver.query.get_or_404(driver_id)
    sessions_data = []
    
    for ds in driver.sessions:
        session = ds.session
        sessions_data.append({
            'session_key': session.session_key,
            'session_name': session.session_name,
            'date_start': session.date_start.isoformat() if session.date_start else None,
            'location': session.location,
            'country_name': session.country_name,
            'circuit_short_name': session.circuit_short_name,
            'year': session.year,
            'position': ds.position,
            'points': ds.points
        })
    
    return jsonify({
        'driver': {
            'id': driver.id,
            'full_name': driver.full_name,
            'driver_number': driver.driver_number
        },
        'sessions': sessions_data
    })

@app.route('/api/sessions', methods=['GET'])
def get_sessions():
    sessions = Session.query.order_by(Session.date_start.desc()).all()
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

@app.route('/api/sync-data', methods=['POST'])
def sync_f1_data():
    try:
        # Get the current year or a specific year
        year = request.json.get('year', 2024) if request.json else 2024
        
        print(f"Starting F1 data sync for year {year}...")
        
        # Fetch drivers data from OpenF1
        drivers_response = requests.get(f"{OPENF1_BASE_URL}/drivers", 
                                      params={'session_key': 'latest'})
        drivers_response.raise_for_status()
        drivers_data = drivers_response.json()
        
        print(f"Fetched {len(drivers_data)} drivers")
        
        # Update drivers
        drivers_updated = 0
        for driver_data in drivers_data:
            driver = Driver.query.filter_by(driver_number=driver_data['driver_number']).first()
            
            if not driver:
                driver = Driver(driver_number=driver_data['driver_number'])
                db.session.add(driver)
                drivers_updated += 1
            
            # Update driver information
            driver.full_name = driver_data.get('full_name', '')
            driver.team_name = driver_data.get('team_name', '')
            driver.team_colour = driver_data.get('team_colour', '')
            driver.country_code = driver_data.get('country_code', '')
            driver.headshot_url = driver_data.get('headshot_url', '')
            driver.last_updated = datetime.utcnow()
        
        # Fetch sessions data
        sessions_response = requests.get(f"{OPENF1_BASE_URL}/sessions", 
                                       params={'year': year})
        sessions_response.raise_for_status()
        sessions_data = sessions_response.json()
        
        print(f"Fetched {len(sessions_data)} sessions")
        
        # Update sessions (limit to recent ones to avoid overwhelming the database)
        sessions_updated = 0
        for session_data in sessions_data[-20:]:  # Last 20 sessions
            session = Session.query.filter_by(session_key=session_data['session_key']).first()
            
            if not session:
                session = Session(session_key=session_data['session_key'])
                db.session.add(session)
                sessions_updated += 1
            
            # Update session information
            session.session_name = session_data.get('session_name', '')
            session.date_start = datetime.fromisoformat(session_data['date_start'].replace('Z', '+00:00')) if session_data.get('date_start') else None
            session.date_end = datetime.fromisoformat(session_data['date_end'].replace('Z', '+00:00')) if session_data.get('date_end') else None
            session.gmt_offset = session_data.get('gmt_offset', '')
            session.session_type = session_data.get('session_type', '')
            session.meeting_key = session_data.get('meeting_key', 0)
            session.location = session_data.get('location', '')
            session.country_name = session_data.get('country_name', '')
            session.circuit_short_name = session_data.get('circuit_short_name', '')
            session.year = session_data.get('year', year)
        
        # Commit the changes
        db.session.commit()
        
        print("F1 data sync completed successfully")
        
        return jsonify({
            'success': True,
            'message': f'Successfully synced F1 data for {year}',
            'drivers_processed': len(drivers_data),
            'sessions_processed': len(sessions_data[-20:]),
            'year': year
        })
        
    except requests.RequestException as e:
        print(f"API request error: {str(e)}")
        return jsonify({
            'success': False,
            'error': f'Failed to fetch data from OpenF1 API: {str(e)}'
        }), 500
    except Exception as e:
        print(f"General error: {str(e)}")
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': f'An error occurred: {str(e)}'
        }), 500

@app.route('/api/stats/summary', methods=['GET'])
def get_stats_summary():
    try:
        total_drivers = Driver.query.count()
        total_sessions = Session.query.count()
        latest_session = Session.query.order_by(Session.date_start.desc()).first()
        
        # Get driver stats
        drivers_with_sessions = db.session.query(Driver).join(DriverSession).distinct().count()
        
        return jsonify({
            'total_drivers': total_drivers,
            'active_drivers': drivers_with_sessions,
            'total_sessions': total_sessions,
            'latest_session': {
                'name': latest_session.session_name if latest_session else None,
                'location': latest_session.location if latest_session else None,
                'date': latest_session.date_start.isoformat() if latest_session and latest_session.date_start else None
            } if latest_session else None,
            'last_sync': Driver.query.order_by(Driver.last_updated.desc()).first().last_updated.isoformat() if Driver.query.first() else None
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/database/reset', methods=['POST'])
def reset_database():
    try:
        # Drop all tables and recreate them
        db.drop_all()
        db.create_all()
        
        return jsonify({
            'success': True,
            'message': 'Database reset successfully'
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'Failed to reset database: {str(e)}'
        }), 500

# Initialize database
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, port=5000)