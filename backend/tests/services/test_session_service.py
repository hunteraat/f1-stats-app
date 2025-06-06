import pytest
from services import session_service
from models import DriverSession
from unittest.mock import ANY


def test_get_all_sessions(mocker, app):
    """
    Tests that the get_all_sessions function returns a list of sessions.
    """
    with app.app_context():
        mock_session = mocker.MagicMock()
        mock_session.to_dict.return_value = {"id": 1, "name": "Test Session"}
        mock_query = mocker.patch("services.session_service.Session.query")
        mock_query.order_by.return_value.all.return_value = [mock_session]

        sessions = session_service.get_all_sessions()

        assert sessions == [{"id": 1, "name": "Test Session"}]
        mock_query.filter.assert_not_called()


def test_get_all_sessions_with_year(mocker, app):
    """
    Tests that the get_all_sessions function returns a list of sessions
    filtered by year.
    """
    with app.app_context():
        mock_session = mocker.MagicMock()
        mock_session.to_dict.return_value = {
            "id": 1,
            "name": "Test Session",
            "year": 2023,
        }
        mock_query = mocker.patch("services.session_service.Session.query")
        mock_query.filter.return_value.order_by.return_value.all.return_value = [
            mock_session
        ]

        sessions = session_service.get_all_sessions(year=2023)

        assert sessions == [{"id": 1, "name": "Test Session", "year": 2023}]
        mock_query.filter.assert_called_once_with(ANY)


def test_get_session_positions(mocker, app):
    """
    Tests that the get_session_positions function returns position data for
    a session.
    """
    with app.app_context():
        mock_driver_session = mocker.MagicMock()
        mock_driver_session.to_dict.return_value = {"id": 1, "driver_id": 1}
        mock_get = mocker.patch("services.session_service.db.session.get")
        mock_get.return_value = mock_driver_session

        mock_position = mocker.MagicMock()
        mock_position.to_dict.return_value = {"id": 1, "position": 1}
        mock_position_query = mocker.patch("services.session_service.Position.query")
        mock_position_chain = mock_position_query.filter_by.return_value
        mock_position_chain.order_by.return_value.all.return_value = [mock_position]

        positions = session_service.get_session_positions(session_id=1)

        assert positions == {
            "driver_session": {"id": 1, "driver_id": 1},
            "positions": [{"id": 1, "position": 1}],
        }
        mock_get.assert_called_once_with(DriverSession, 1)
        mock_position_query.filter_by.assert_called_once_with(driver_session_id=1)


def test_get_session_positions_no_session(mocker, app):
    """
    Tests that the get_session_positions function returns None when the session
    is not found.
    """
    with app.app_context():
        mock_get = mocker.patch("services.session_service.db.session.get")
        mock_get.return_value = None

        positions = session_service.get_session_positions(session_id=1)

        assert positions is None
        mock_get.assert_called_once_with(DriverSession, 1)


def test_get_session_positions_no_session_id():
    """
    Tests that the get_session_positions function raises a ValueError when no
    session_id is provided.
    """
    with pytest.raises(ValueError, match="session_id parameter is required"):
        session_service.get_session_positions(session_id=None)
