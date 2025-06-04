# API Configuration
OPENF1_BASE_URL = "https://api.openf1.org/v1"

# Database Configuration
SQLALCHEMY_DATABASE_URI = 'sqlite:///f1_stats.db'
SQLALCHEMY_TRACK_MODIFICATIONS = False

# CORS Configuration
CORS_HEADERS = {
    'Access-Control-Allow-Origin': '*',
    'Access-Control-Allow-Headers': 'Content-Type,Authorization',
    'Access-Control-Allow-Methods': 'GET,PUT,POST,DELETE,OPTIONS'
} 