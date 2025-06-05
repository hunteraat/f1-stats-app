"""Routes package initialization"""

# flake8: noqa: E402
from flask import Blueprint

# Define blueprints
ai_bp = Blueprint("ai", __name__)
constructors_bp = Blueprint("constructors", __name__)
drivers_bp = Blueprint("drivers", __name__)
overview_bp = Blueprint("overview", __name__)
sessions_bp = Blueprint("sessions", __name__)
sync_bp = Blueprint("sync", __name__)
years_bp = Blueprint("years", __name__)

# Import routes after blueprint definition to avoid circular imports
from . import ai, constructors, drivers, overview, sessions, sync, years  # noqa: F401

__all__ = [
    "ai_bp",
    "constructors_bp",
    "drivers_bp",
    "overview_bp",
    "sessions_bp",
    "sync_bp",
    "years_bp",
]
