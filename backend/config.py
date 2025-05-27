import os

# Points system
RACE_POINTS = {
    1: 25,
    2: 18,
    3: 15,
    4: 12,
    5: 10,
    6: 8,
    7: 6,
    8: 4,
    9: 2,
    10: 1
}

SPRINT_POINTS = {
    1: 8,
    2: 7,
    3: 6,
    4: 5,
    5: 4,
    6: 3,
    7: 2,
    8: 1
}

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