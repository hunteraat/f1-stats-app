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
    final_position = db.Column(db.Integer, nullable=True)
    points = db.Column(db.Float, nullable=True)
    
    # Relationships
    driver = db.relationship('Driver', back_populates='sessions')
    session = db.relationship('Session', back_populates='driver_sessions')
    positions = db.relationship('Position', back_populates='driver_session', cascade='all, delete-orphan')
    
    # Unique constraint to prevent duplicate driver-session combinations
    __table_args__ = (db.UniqueConstraint('driver_id', 'session_id'),)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_session_id = db.Column(db.Integer, db.ForeignKey('driver_session.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    
    # Relationship
    driver_session = db.relationship('DriverSession', back_populates='positions')

class YearData(db.Model):
    """Track which years have been synced to avoid re-downloading"""
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, nullable=False)
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    drivers_count = db.Column(db.Integer, default=0)
    sessions_count = db.Column(db.Integer, default=0)

# OpenF1 API base URL
OPENF1_BASE_URL = "https://api.openf1.org/v1"

@app.route('/')
def home():
    return jsonify({"message": "F1 Statistics API is running!"})

@app.route('/api/years', methods=['GET'])
def get_available_years():
    """Get list of years with sync status"""
    years = []
    synced_years = {yd.year: yd for yd in YearData.query.all()}
    
    for year in range(2000, 2026):
        year_info = {
            'year': year,
            'synced': year in synced_years,
            'last_synced': synced_years[year].last_synced.isoformat() if year in synced_years else None,
            'drivers_count': synced_years[year].drivers_count if year in synced_years else 0,
            'sessions_count': synced_years[year].sessions_count if year in synced_years else 0
        }
        years.append(year_info)
    
    return jsonify(years)

@app.route('/api/drivers', methods=['GET'])
def get_drivers():
    year = request.args.get('year', type=int)
    
    if year:
        # Filter drivers by sessions in the specified year
        drivers = db.session.query(Driver).join(DriverSession).join(Session).filter(Session.year == year).distinct().all()
    else:
        drivers = Driver.query.all()
    
    drivers_data = []
    for driver in drivers:
        # Calculate stats for the driver
        if year:
            sessions = [ds for ds in driver.sessions if ds.session.year == year]
        else:
            sessions = driver.sessions
            
        # Calculate wins and podiums
        wins = sum(1 for ds in sessions if ds.final_position == 1)
        podiums = sum(1 for ds in sessions if ds.final_position and ds.final_position <= 3)
        
        drivers_data.append({
            'id': driver.id,
            'driver_number': driver.driver_number,
            'full_name': driver.full_name,
            'team_name': driver.team_name,
            'team_colour': driver.team_colour,
            'country_code': driver.country_code,
            'headshot_url': driver.headshot_url,
            'last_updated': driver.last_updated.isoformat() if driver.last_updated else None,
            'session_count': len(sessions),
            'wins': wins,
            'podiums': podiums
        })
    
    return jsonify(drivers_data)

@app.route('/api/drivers/<int:driver_id>/sessions', methods=['GET'])
def get_driver_sessions(driver_id):
    year = request.args.get('year', type=int)
    driver = Driver.query.get_or_404(driver_id)
    
    sessions_data = []
    driver_sessions = driver.sessions
    
    if year:
        driver_sessions = [ds for ds in driver_sessions if ds.session.year == year]
    
    for ds in driver_sessions:
        session = ds.session
        sessions_data.append({
            'id': ds.id,
            'session_key': session.session_key,
            'session_name': session.session_name,
            'date_start': session.date_start.isoformat() if session.date_start else None,
            'location': session.location,
            'country_name': session.country_name,
            'circuit_short_name': session.circuit_short_name,
            'year': session.year,
            'final_position': ds.final_position,
            'points': ds.points
        })
    
    return jsonify({
        'driver': {
            'id': driver.id,
            'full_name': driver.full_name,
            'driver_number': driver.driver_number,
            'headshot_url': driver.headshot_url
        },
        'sessions': sessions_data
    })

@app.route('/api/sessions/<int:session_id>/positions', methods=['GET'])
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

@app.route('/api/sessions', methods=['GET'])
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

@app.route('/api/sync-data/<int:year>', methods=['POST'])
def sync_f1_data(year):
    try:
        # Check if year is already synced
        year_data = YearData.query.filter_by(year=year).first()
        if year_data:
            return jsonify({
                'success': True,
                'message': f'Data for {year} already exists',
                'cached': True,
                'year': year
            })
        
        print(f"Starting F1 data sync for year {year}...")
        
        # Fetch sessions for the year first
        sessions_response = requests.get(f"{OPENF1_BASE_URL}/sessions", 
                                       params={'year': year})
        sessions_response.raise_for_status()
        sessions_data = sessions_response.json()
        
        if not sessions_data:
            return jsonify({
                'success': False,
                'error': f'No sessions found for year {year}'
            }), 404
        
        print(f"Fetched {len(sessions_data)} sessions for {year}")
        
        # Process sessions
        sessions_processed = 0
        drivers_encountered = set()
        
        for session_data in sessions_data:
            session = Session.query.filter_by(session_key=session_data['session_key']).first()
            
            if not session:
                session = Session(session_key=session_data['session_key'])
                db.session.add(session)
                sessions_processed += 1
            
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
            session.year = year
            
            # Fetch drivers for this session
            try:
                drivers_response = requests.get(f"{OPENF1_BASE_URL}/drivers", 
                                              params={'session_key': session_data['session_key']})
                drivers_response.raise_for_status()
                session_drivers = drivers_response.json()
                
                for driver_data in session_drivers:
                    driver_number = driver_data['driver_number']
                    drivers_encountered.add(driver_number)
                    
                    # Get or create driver
                    driver = Driver.query.filter_by(driver_number=driver_number).first()
                    if not driver:
                        driver = Driver(driver_number=driver_number)
                        db.session.add(driver)
                    
                    # Update driver information
                    driver.full_name = driver_data.get('full_name', '')
                    driver.team_name = driver_data.get('team_name', '')
                    driver.team_colour = driver_data.get('team_colour', '')
                    driver.country_code = driver_data.get('country_code', '')
                    driver.headshot_url = driver_data.get('headshot_url', '')
                    driver.last_updated = datetime.utcnow()
                    
                    # Create or update driver session
                    driver_session = DriverSession.query.filter_by(
                        driver_id=driver.id, 
                        session_id=session.id
                    ).first()
                    
                    if not driver_session:
                        driver_session = DriverSession(
                            driver_id=driver.id,
                            session_id=session.id
                        )
                        db.session.add(driver_session)
                    
                    # Fetch position data for this driver and session
                    try:
                        position_response = requests.get(f"{OPENF1_BASE_URL}/position", 
                                                       params={
                                                           'session_key': session_data['session_key'],
                                                           'driver_number': driver_number
                                                       })
                        position_response.raise_for_status()
                        position_data = position_response.json()
                        
                        if position_data:
                            # Clear existing positions for this driver session
                            Position.query.filter_by(driver_session_id=driver_session.id).delete()
                            
                            # Add new position data
                            final_position = None
                            latest_date = None
                            
                            for pos in position_data:
                                pos_date = datetime.fromisoformat(pos['date'].replace('Z', '+00:00'))
                                position = Position(
                                    driver_session_id=driver_session.id,
                                    date=pos_date,
                                    position=pos['position']
                                )
                                db.session.add(position)
                                
                                # Track the final position (latest date)
                                if not latest_date or pos_date > latest_date:
                                    latest_date = pos_date
                                    final_position = pos['position']
                            
                            driver_session.final_position = final_position
                        
                    except requests.RequestException as e:
                        print(f"Failed to fetch position data for driver {driver_number} in session {session_data['session_key']}: {e}")
                        continue
                
            except requests.RequestException as e:
                print(f"Failed to fetch drivers for session {session_data['session_key']}: {e}")
                continue
        
        # Create year data record
        year_data = YearData(
            year=year,
            drivers_count=len(drivers_encountered),
            sessions_count=sessions_processed,
            last_synced=datetime.utcnow()
        )
        db.session.add(year_data)
        
        # Commit all changes
        db.session.commit()
        
        print(f"F1 data sync completed successfully for {year}")
        
        return jsonify({
            'success': True,
            'message': f'Successfully synced F1 data for {year}',
            'drivers_processed': len(drivers_encountered),
            'sessions_processed': sessions_processed,
            'year': year,
            'cached': False
        })
        
    except requests.RequestException as e:
        print(f"API request error: {str(e)}")
        db.session.rollback()
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
        year = request.args.get('year', type=int)
        
        if year:
            # Year-specific stats
            total_drivers = db.session.query(Driver).join(DriverSession).join(Session).filter(Session.year == year).distinct().count()
            total_sessions = Session.query.filter(Session.year == year).count()
            latest_session = Session.query.filter(Session.year == year).order_by(Session.date_start.desc()).first()
        else:
            # Overall stats
            total_drivers = Driver.query.count()
            total_sessions = Session.query.count()
            latest_session = Session.query.order_by(Session.date_start.desc()).first()
        
        # Get driver stats
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

@app.route('/api/database/reset', methods=['POST'])
def reset_database():
    with app.app_context():
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
    #reset_database()