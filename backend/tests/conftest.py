import pytest

from app import create_app
from extensions import db


@pytest.fixture(scope="module")
def app():
    """
    Fixture that creates a test Flask app instance with a temporary
    in-memory SQLite database.
    """
    # Create a test app instance
    app = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
            "WTF_CSRF_ENABLED": False,  # Disable CSRF for testing forms
        }
    )

    # Establish an application context before creating the database tables
    with app.app_context():
        # Create the database and the database table(s)
        db.create_all()

        yield app  # this is where the testing happens

        # Drop the database table(s)
        db.drop_all()


@pytest.fixture(scope="module")
def client(app):
    """
    Fixture that provides a test client for the Flask app.
    """
    return app.test_client()
