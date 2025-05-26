from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import requests
import json
import time

app = Flask(__name__)
CORS(app)

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///f1_data.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
pointsDic = {1:25,2:18,3:15,4:12,5:10,6:8,7:6,8:4,9:2,10:1}
sprintPointsDic = {1:8,2:7,3:6,4:5,5:4,6:3,7:2,8:1}

# Database Models (keeping the same models as before)
class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_number = db.Column(db.Integer, unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(50), nullable=True)
    team_colour = db.Column(db.String(7), nullable=True)
    country_code = db.Column(db.String(3), nullable=True)
    headshot_url = db.Column(db.String(255), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    
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
    
    driver_sessions = db.relationship('DriverSession', back_populates='session', cascade='all, delete-orphan')

class DriverSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey('driver.id'), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey('session.id'), nullable=False)
    final_position = db.Column(db.Integer, nullable=True)
    
    driver = db.relationship('Driver', back_populates='sessions')
    session = db.relationship('Session', back_populates='driver_sessions')
    positions = db.relationship('Position', back_populates='driver_session', cascade='all, delete-orphan')
    
    __table_args__ = (db.UniqueConstraint('driver_id', 'session_id'),)

class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_session_id = db.Column(db.Integer, db.ForeignKey('driver_session.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    position = db.Column(db.Integer, nullable=False)
    
    driver_session = db.relationship('DriverSession', back_populates='positions')

class YearData(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, nullable=False)
    last_synced = db.Column(db.DateTime, default=datetime.utcnow)
    drivers_count = db.Column(db.Integer, default=0)
    sessions_count = db.Column(db.Integer, default=0)

# OpenF1 API base URL
OPENF1_BASE_URL = "https://api.openf1.org/v1"

def make_api_request_with_retry(url, params=None, max_retries=3, delay=1):
    """Make API request with retry logic and rate limiting"""
    for attempt in range(max_retries):
        try:
            time.sleep(delay)  # Add delay between requests to avoid rate limiting
            response = requests.get(url, params=params, timeout=30)
            
            if response.status_code == 429:  # Rate limited
                wait_time = min(2 ** attempt, 10)  # Exponential backoff, max 10 seconds
                print(f"Rate limited, waiting {wait_time} seconds...")
                time.sleep(wait_time)
                continue
                
            response.raise_for_status()
            return response.json()
            
        except requests.RequestException as e:
            if attempt == max_retries - 1:
                raise e
            print(f"Request failed (attempt {attempt + 1}), retrying in {delay * (attempt + 1)} seconds...")
            time.sleep(delay * (attempt + 1))
    
    return None

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
        drivers = db.session.query(Driver).join(DriverSession).join(Session).filter(Session.year == year).distinct().all()
    else:
        drivers = Driver.query.all()
    
    # First, calculate total points for all drivers to determine standings
    drivers_points = []
    for driver in drivers:
        if year:
            sessions = [ds for ds in driver.sessions if ds.session.year == year]
            race_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Race' and ds.final_position is not None]
            sprint_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Sprint' and ds.final_position is not None]
            
            total_points = 0
            for ds in race_sessions:
                if ds.final_position in pointsDic:
                    total_points += pointsDic[ds.final_position]
            
            for ds in sprint_sessions:
                if ds.final_position in sprintPointsDic:
                    total_points += sprintPointsDic[ds.final_position]
            
            drivers_points.append((driver, total_points))
        else:
            sessions = driver.sessions
            race_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Race' and ds.final_position is not None]
            sprint_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Sprint' and ds.final_position is not None]
            
            total_points = 0
            for ds in race_sessions:
                if ds.final_position in pointsDic:
                    total_points += pointsDic[ds.final_position]
            
            for ds in sprint_sessions:
                if ds.final_position in sprintPointsDic:
                    total_points += sprintPointsDic[ds.final_position]
            
            drivers_points.append((driver, total_points))
    
    # Sort drivers by points to determine standings
    drivers_points.sort(key=lambda x: x[1], reverse=True)
    standings = {driver: pos+1 for pos, (driver, _) in enumerate(drivers_points)}
    
    drivers_data = []
    for driver, total_points in drivers_points:
        if year:
            sessions = [ds for ds in driver.sessions if ds.session.year == year]
            race_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Race' and ds.final_position is not None]
            sprint_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Sprint' and ds.final_position is not None]
            
            # Calculate wins and podiums from race sessions only
            wins = sum(1 for ds in race_sessions if ds.final_position == 1)
            podiums = sum(1 for ds in race_sessions if ds.final_position <= 3)
        else:
            sessions = driver.sessions
            race_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Race' and ds.final_position is not None]
            sprint_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Sprint' and ds.final_position is not None]
            wins = sum(1 for ds in race_sessions if ds.final_position == 1)
            podiums = sum(1 for ds in race_sessions if ds.final_position <= 3)
        
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
            'race_count': len(race_sessions),
            'wins': wins,
            'podiums': podiums,
            'points': total_points,
            'standing_position': standings[driver]
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
        # Calculate points based on session type
        points = 0
        if ds.final_position:
            if session.session_name == 'Race' and ds.final_position in pointsDic:
                points = pointsDic[ds.final_position]
            elif session.session_name == 'Sprint' and ds.final_position in sprintPointsDic:
                points = sprintPointsDic[ds.final_position]
        
        sessions_data.append({
            'id': ds.id,
            'session_key': session.session_key,
            'session_name': session.session_name,
            'session_type': session.session_type,
            'date_start': session.date_start.isoformat() if session.date_start else None,
            'location': session.location,
            'country_name': session.country_name,
            'circuit_short_name': session.circuit_short_name,
            'year': session.year,
            'final_position': ds.final_position,
            'points': points
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
        
        print(f"Starting optimized F1 data sync for year {year}...")
        
        # STEP 1: Fetch all sessions for the year (single API call)
        print("Fetching sessions...")
        sessions_data = make_api_request_with_retry(f"{OPENF1_BASE_URL}/sessions", {'year': year})
        
        if not sessions_data:
            return jsonify({
                'success': False,
                'error': f'No sessions found for year {year}'
            }), 404
        
        print(f"Fetched {len(sessions_data)} sessions for {year}")
        
        # STEP 2: Fetch drivers for each session in batches
        print("Fetching drivers...")
        all_drivers_data = []
        session_keys = [session['session_key'] for session in sessions_data]
        
        # Process in batches to avoid too many requests
        for i in range(0, len(session_keys), 5):  # Process 5 sessions at a time
            batch_keys = session_keys[i:i+5]
            for session_key in batch_keys:
                try:
                    session_drivers = make_api_request_with_retry(
                        f"{OPENF1_BASE_URL}/drivers", 
                        {'session_key': session_key}
                    )
                    if session_drivers:
                        all_drivers_data.extend(session_drivers)
                except Exception as e:
                    print(f"Failed to fetch drivers for session {session_key}: {e}")
                    continue
        
        # Remove duplicates based on driver_number
        unique_drivers = {}
        for driver in all_drivers_data:
            driver_num = driver.get('driver_number')
            if driver_num and driver_num not in unique_drivers:
                unique_drivers[driver_num] = driver
        all_drivers_data = list(unique_drivers.values())
        
        print(f"Fetched {len(all_drivers_data)} unique drivers")
        
        # STEP 3: Fetch position data for each session
        print("Fetching position data...")
        all_positions_data = []
        
        for i in range(0, len(session_keys), 5):  # Process 5 sessions at a time
            batch_keys = session_keys[i:i+5]
            for session_key in batch_keys:
                try:
                    session_positions = make_api_request_with_retry(
                        f"{OPENF1_BASE_URL}/position",
                        {'session_key': session_key}
                    )
                    if session_positions:
                        all_positions_data.extend(session_positions)
                except Exception as e:
                    print(f"Failed to fetch positions for session {session_key}: {e}")
                    continue
        
        print(f"Fetched {len(all_positions_data)} position records")
        
        # STEP 4: Process and store data
        sessions_processed = 0
        drivers_encountered = set()
        
        # Create driver lookup
        driver_lookup = {d['driver_number']: d for d in all_drivers_data}
        
        # Group positions by session_key and driver_number for efficient lookup
        positions_by_session_driver = {}
        for pos in all_positions_data:
            session_key = pos.get('session_key')
            driver_number = pos.get('driver_number')
            if session_key and driver_number:
                key = (session_key, driver_number)
                if key not in positions_by_session_driver:
                    positions_by_session_driver[key] = []
                positions_by_session_driver[key].append(pos)
        
        # Process sessions
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
            
            # Process drivers for this session
            for driver_number, driver_data in driver_lookup.items():
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
                
                # Process position data for this driver and session
                position_key = (session_data['session_key'], driver_number)
                if position_key in positions_by_session_driver:
                    position_data = positions_by_session_driver[position_key]
                    
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
                    # Points are now calculated only during retrieval
        
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
        
        print(f"Optimized F1 data sync completed successfully for {year}")
        
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
            total_drivers = db.session.query(Driver).join(DriverSession).join(Session).filter(Session.year == year).distinct().count()
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