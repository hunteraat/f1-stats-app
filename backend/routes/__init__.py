"""Routes package initialization"""
from flask import Blueprint

# Create blueprint instances
drivers_bp = Blueprint('drivers', __name__)
sessions_bp = Blueprint('sessions', __name__)
sync_bp = Blueprint('sync', __name__)
overview_bp = Blueprint('overview', __name__)
years_bp = Blueprint('years', __name__)
constructors_bp = Blueprint('constructors', __name__)
ai_bp = Blueprint('ai', __name__)

# Import views to register routes
from .drivers import *  # This will use the blueprint instance defined above
from .sessions import *
from .sync import *
from .overview import *
from .years import *
from .constructors import *
from .ai import *

__all__ = ['drivers_bp', 'sessions_bp', 'sync_bp', 'overview_bp', 'years_bp', 'constructors_bp', 'ai_bp'] 