"""Routes package initialization"""
from flask import Blueprint

# Create blueprint instances
drivers_bp = Blueprint('drivers', __name__)
sessions_bp = Blueprint('sessions', __name__)
sync_bp = Blueprint('sync', __name__)
stats_bp = Blueprint('stats', __name__)
years_bp = Blueprint('years', __name__)

# Import views to register routes
from .drivers import *  # This will use the blueprint instance defined above
from .sessions import *
from .sync import *
from .stats import *
from .years import *

__all__ = ['drivers_bp', 'sessions_bp', 'sync_bp', 'stats_bp', 'years_bp'] 