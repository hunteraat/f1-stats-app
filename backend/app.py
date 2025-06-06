import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify

from extensions import db, migrate, cors
from config import config
from views import register_view_creation


def setup_logging(app):
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    if not os.path.exists("logs"):
        os.makedirs("logs")

    # Set up file handler for all logs
    log_file = os.path.join("logs", "f1_stats.log")
    file_handler = RotatingFileHandler(log_file, maxBytes=1024 * 1024, backupCount=10)
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s: %(message)s " + "[in %(pathname)s:%(lineno)d]"
        )
    )

    if app.debug:
        file_handler.setLevel(logging.DEBUG)
    else:
        file_handler.setLevel(logging.INFO)

    app.logger.addHandler(file_handler)
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.info("F1 Stats startup")


def register_blueprints(app):
    """Register Flask blueprints"""
    from routes import (
        drivers_bp,
        sessions_bp,
        sync_bp,
        overview_bp,
        years_bp,
        constructors_bp,
        ai_bp,
    )

    app.register_blueprint(drivers_bp, url_prefix="/api/drivers")
    app.register_blueprint(sessions_bp, url_prefix="/api/sessions")
    app.register_blueprint(sync_bp, url_prefix="/api/sync")
    app.register_blueprint(overview_bp, url_prefix="/api/overview")
    app.register_blueprint(years_bp, url_prefix="/api/years")
    app.register_blueprint(constructors_bp, url_prefix="/api/constructors")
    app.register_blueprint(ai_bp, url_prefix="/api/ai")


def create_app(config_data=None):
    """Create and configure the Flask application"""
    app = Flask(__name__)

    if config_data and isinstance(config_data, dict):
        app.config.from_mapping(config_data)
    else:
        config_name = config_data or os.environ.get("FLASK_ENV", "default")
        app.config.from_object(config[config_name])
        if config_name in config:
            config[config_name].init_app(app)

    # Configure Flask to not redirect on missing trailing slashes
    app.url_map.strict_slashes = False

    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)

    # Set up logging
    if not app.testing:
        setup_logging(app)

    # Register blueprints
    register_blueprints(app)

    # Register view creation event listener
    register_view_creation(app)

    @app.route("/")
    def home():
        return jsonify({"message": "F1 Statistics API is running!"})

    return app


# The following is now managed by the flask command or a run.py script
# We will leave it here for now for `python app.py` to work during transition
app = create_app()

if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        app.logger.info("Database tables ready")
    app.run(debug=app.config["DEBUG"])
