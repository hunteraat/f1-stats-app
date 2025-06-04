import os
import logging
from logging.handlers import RotatingFileHandler
from flask import Flask, jsonify

from extensions import db, migrate, cors
from config import SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS

def setup_logging(app):
    """Configure logging for the application"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Set up file handler for all logs
    file_handler = RotatingFileHandler('logs/f1_stats.log', maxBytes=1024 * 1024, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'
    ))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    # Set up console handler for debug logs
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(logging.Formatter('%(levelname)s: %(message)s'))
    if app.debug:
        console_handler.setLevel(logging.DEBUG)
    else:
        console_handler.setLevel(logging.INFO)
    app.logger.addHandler(console_handler)

    # Set overall logging level
    app.logger.setLevel(logging.DEBUG if app.debug else logging.INFO)
    app.logger.info('F1 Stats startup')

def register_blueprints(app):
    """Register Flask blueprints"""
    from routes import drivers_bp, sessions_bp, sync_bp, overview_bp, years_bp, constructors_bp, ai_bp
    
    app.register_blueprint(drivers_bp, url_prefix='/api/drivers')
    app.register_blueprint(sessions_bp, url_prefix='/api/sessions')
    app.register_blueprint(sync_bp, url_prefix='/api/sync')
    app.register_blueprint(overview_bp, url_prefix='/api/overview')
    app.register_blueprint(years_bp, url_prefix='/api/years')
    app.register_blueprint(constructors_bp, url_prefix='/api/constructors')
    app.register_blueprint(ai_bp, url_prefix='/api/ai')

def create_app(debug=False):
    """Create and configure the Flask application"""
    app = Flask(__name__)
    app.debug = debug
    
    # Configure Flask to not redirect on missing trailing slashes
    app.url_map.strict_slashes = False
    
    # Configure SQLite database
    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
    
    # Initialize extensions
    db.init_app(app)
    migrate.init_app(app, db)
    cors.init_app(app)
    
    # Set up logging
    setup_logging(app)
    
    # Register blueprints
    register_blueprints(app)
    
    @app.route('/')
    def home():
        return jsonify({"message": "F1 Statistics API is running!"})
    
    return app

# Create the application instance
app = create_app(debug=True)

# Create database tables within application context
with app.app_context():
    db.create_all()
    app.logger.info("Database tables ready")

if __name__ == '__main__':
    app.run(debug=True)