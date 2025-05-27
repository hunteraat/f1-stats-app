import os
import sys
from flask import Blueprint, jsonify
from sqlalchemy import func

# Handle imports based on where we're running from
try:
    # Try local imports first
    from models import db, YearData
    from utils import add_cors_headers
except ImportError:
    # If local imports fail, try package imports
    if os.path.basename(os.getcwd()) == 'backend':
        sys.path.insert(0, os.path.dirname(os.getcwd()))
    from backend.models import db, YearData
    from backend.utils import add_cors_headers

years_bp = Blueprint('years', __name__)
years_bp = add_cors_headers(years_bp)

@years_bp.route('/', methods=['GET'])
def get_available_years():
    """Get list of years with sync status"""
    years = []
    synced_years = {yd.year: yd for yd in YearData.query.all()}
    
    for year in range(2018, 2026):
        year_info = {
            'year': year,
            'synced': year in synced_years,
            'last_synced': synced_years[year].last_synced.isoformat() if year in synced_years else None,
            'drivers_count': synced_years[year].drivers_count if year in synced_years else 0,
            'sessions_count': synced_years[year].sessions_count if year in synced_years else 0
        }
        years.append(year_info)
    
    return jsonify(years) 