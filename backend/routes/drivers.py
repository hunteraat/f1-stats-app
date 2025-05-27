from flask import Blueprint, jsonify, request
from sqlalchemy import func, and_
from extensions import db
from models import Driver, Session, DriverSession, Position, Lap
from config import RACE_POINTS, SPRINT_POINTS
from utils import add_cors_headers
from . import drivers_bp

drivers_bp = add_cors_headers(drivers_bp)

def calculate_and_save_final_position(driver_session):
    """Calculate and save the final position for a driver session if it doesn't exist."""
    if driver_session.final_position is None:
        # Get the last position record for this driver session
        last_position = Position.query.filter_by(
            driver_session_id=driver_session.id
        ).order_by(Position.date.desc()).first()
        
        if last_position:
            driver_session.final_position = last_position.position
            try:
                db.session.commit()
            except:
                db.session.rollback()

def calculate_and_save_fastest_lap(driver_session):
    """Calculate and save the fastest lap flag for a driver session if it's a race session."""
    if driver_session.session.session_type == 'Race':
        # Get all laps for this session by joining through DriverSession
        session_laps = Lap.query.join(
            DriverSession, Lap.driver_session_id == DriverSession.id
        ).filter(
            DriverSession.session_id == driver_session.session_id,
            Lap.lap_time.isnot(None)  # Exclude null lap times
        ).all()
        
        if session_laps:
            # Find the fastest lap
            fastest_lap = min(session_laps, key=lambda x: x.lap_time)
            
            # Update fastest_lap flag for all driver sessions in this race
            driver_sessions = DriverSession.query.filter_by(session_id=driver_session.session_id).all()
            for ds in driver_sessions:
                ds.fastest_lap = False
                if ds.id == fastest_lap.driver_session_id:
                    ds.fastest_lap = True
            
            try:
                db.session.commit()
            except:
                db.session.rollback()

@drivers_bp.route('/', methods=['GET'])
def get_drivers():
    year = request.args.get('year', type=int)
    
    if year:
        drivers = db.session.query(Driver).join(DriverSession).join(Session).filter(Session.year == year).distinct().all()
    else:
        drivers = Driver.query.all()
    
    # First, calculate final positions and fastest laps for any sessions that don't have them
    for driver in drivers:
        sessions = driver.sessions if not year else [ds for ds in driver.sessions if ds.session.year == year]
        for ds in sessions:
            if ds.final_position is None:
                calculate_and_save_final_position(ds)
            calculate_and_save_fastest_lap(ds)
    
    # Now calculate total points for all drivers to determine standings
    drivers_points = []
    teams_points = {}
    
    for driver in drivers:
        if year:
            sessions = [ds for ds in driver.sessions if ds.session.year == year]
            race_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Race' and ds.final_position is not None]
            sprint_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Sprint' and ds.final_position is not None]

            total_points = 0
            for ds in race_sessions:
                if ds.final_position in RACE_POINTS:
                    total_points += RACE_POINTS[ds.final_position]
            
            for ds in sprint_sessions:
                if ds.final_position in SPRINT_POINTS:
                    total_points += SPRINT_POINTS[ds.final_position]
            
            drivers_points.append((driver, total_points))
            
            # Accumulate team points
            if driver.team_name:
                if driver.team_name not in teams_points:
                    teams_points[driver.team_name] = 0
                teams_points[driver.team_name] += total_points
        else:
            sessions = driver.sessions
            race_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Race' and ds.final_position is not None]
            sprint_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Sprint' and ds.final_position is not None]
            all_race_types = race_sessions + sprint_sessions
            wins = sum(1 for ds in all_race_types if ds.final_position == 1)
            podiums = sum(1 for ds in all_race_types if ds.final_position <= 3)
            fastest_laps = sum(1 for ds in all_race_types if ds.fastest_lap)
            
            total_points = 0
            for ds in race_sessions:
                if ds.final_position in RACE_POINTS:
                    total_points += RACE_POINTS[ds.final_position]
            
            for ds in sprint_sessions:
                if ds.final_position in SPRINT_POINTS:
                    total_points += SPRINT_POINTS[ds.final_position]
            
            drivers_points.append((driver, total_points))
            
            # Accumulate team points
            if driver.team_name:
                if driver.team_name not in teams_points:
                    teams_points[driver.team_name] = 0
                teams_points[driver.team_name] += total_points
    
    # Sort drivers by points to determine standings
    drivers_points.sort(key=lambda x: x[1], reverse=True)
    standings = {driver: pos+1 for pos, (driver, _) in enumerate(drivers_points)}
    
    # Sort teams by points to determine constructor standings
    sorted_teams = sorted(teams_points.items(), key=lambda x: x[1], reverse=True)
    constructor_standings = {team: pos+1 for pos, (team, _) in enumerate(sorted_teams)}
    
    drivers_data = []
    for driver, total_points in drivers_points:
        if year:
            sessions = [ds for ds in driver.sessions if ds.session.year == year]
            race_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Race' and ds.final_position is not None]
            sprint_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Sprint' and ds.final_position is not None]
            
            # Calculate wins, podiums, and fastest laps from both race and sprint sessions
            all_race_types = race_sessions + sprint_sessions
            wins = sum(1 for ds in all_race_types if ds.final_position == 1)
            podiums = sum(1 for ds in all_race_types if ds.final_position <= 3)
            fastest_laps = sum(1 for ds in all_race_types if ds.fastest_lap)
        else:
            sessions = driver.sessions
            race_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Race' and ds.final_position is not None]
            sprint_sessions = [ds for ds in sessions if ds.session.session_type == 'Race' and ds.session.session_name == 'Sprint' and ds.final_position is not None]
            all_race_types = race_sessions + sprint_sessions
            wins = sum(1 for ds in all_race_types if ds.final_position == 1)
            podiums = sum(1 for ds in all_race_types if ds.final_position <= 3)
            fastest_laps = sum(1 for ds in all_race_types if ds.fastest_lap)
        
        # Get team points and constructor position
        team_points = teams_points.get(driver.team_name, 0)
        constructor_position = constructor_standings.get(driver.team_name, None)
        
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
            'fastest_laps': fastest_laps,
            'points': total_points,
            'standing_position': standings[driver],
            'team_points': team_points,
            'constructor_position': constructor_position
        })
    
    return jsonify(drivers_data)

@drivers_bp.route('/<int:driver_id>/sessions', methods=['GET'])
def get_driver_sessions(driver_id):
    year = request.args.get('year', type=int)
    driver = Driver.query.get_or_404(driver_id)
    
    driver_sessions = driver.sessions
    
    if year:
        driver_sessions = [ds for ds in driver_sessions if ds.session.year == year]
    
    # Calculate final positions and fastest laps for any sessions that don't have them
    for ds in driver_sessions:
        if ds.final_position is None:
            calculate_and_save_final_position(ds)
        calculate_and_save_fastest_lap(ds)
    
    sessions_data = []
    for ds in driver_sessions:
        session = ds.session
        # Calculate points based on session type
        points = 0
        if ds.final_position:
            if session.session_name == 'Race' and ds.final_position in RACE_POINTS:
                points = RACE_POINTS[ds.final_position]
                if ds.fastest_lap and ds.final_position <= 10:  # Only award fastest lap point if in top 10
                    points += 1
            elif session.session_name == 'Sprint' and ds.final_position in SPRINT_POINTS:
                points = SPRINT_POINTS[ds.final_position]
        
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
            'fastest_lap': ds.fastest_lap,
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