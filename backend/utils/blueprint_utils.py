import os
import sys

# Handle imports based on where we're running from
try:
    # Try local imports first
    from config import CORS_HEADERS
except ImportError:
    # If local imports fail, try package imports
    if os.path.basename(os.getcwd()) == 'backend':
        sys.path.insert(0, os.path.dirname(os.getcwd()))
    from backend.config import CORS_HEADERS

def add_cors_headers(blueprint):
    """Add CORS headers to a blueprint's responses"""
    @blueprint.after_request
    def after_request(response):
        for header, value in CORS_HEADERS.items():
            response.headers.add(header, value)
        return response
    return blueprint 