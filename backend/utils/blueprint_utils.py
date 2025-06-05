from config import CORS_HEADERS


def add_cors_headers(blueprint):
    """Add CORS headers to a blueprint's responses"""

    @blueprint.after_request
    def after_request(response):
        for header, value in CORS_HEADERS.items():
            response.headers.add(header, value)
        return response

    return blueprint
