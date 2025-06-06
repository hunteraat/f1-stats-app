from unittest.mock import patch


def test_get_sessions(client):
    """
    Tests the /sessions endpoint.
    """
    with patch(
        "routes.sessions.session_service.get_all_sessions"
    ) as mock_get_all_sessions:
        mock_get_all_sessions.return_value = [{"name": "Test Session"}]
        response = client.get("/api/sessions")
        assert response.status_code == 200
        assert response.json == [{"name": "Test Session"}]
        mock_get_all_sessions.assert_called_once_with(None)


def test_get_sessions_with_year(client):
    """
    Tests the /sessions endpoint with a year filter.
    """
    with patch(
        "routes.sessions.session_service.get_all_sessions"
    ) as mock_get_all_sessions:
        mock_get_all_sessions.return_value = [{"name": "Test Session 2023"}]
        response = client.get("/api/sessions?year=2023")
        assert response.status_code == 200
        assert response.json == [{"name": "Test Session 2023"}]
        mock_get_all_sessions.assert_called_once_with(2023)


def test_get_session_positions(client):
    """
    Tests the /sessions/<session_id>/positions endpoint.
    """
    with patch(
        "routes.sessions.session_service.get_session_positions"
    ) as mock_get_session_positions:
        mock_get_session_positions.return_value = {
            "driver_session": {},
            "positions": [],
        }
        response = client.get("/api/sessions/1/positions")
        assert response.status_code == 200
        assert response.json == {"driver_session": {}, "positions": []}
        mock_get_session_positions.assert_called_once_with(1)


def test_get_session_positions_not_found(client):
    """
    Tests the /sessions/<session_id>/positions endpoint when the session is not found.
    """
    with patch(
        "routes.sessions.session_service.get_session_positions"
    ) as mock_get_session_positions:
        mock_get_session_positions.return_value = None
        response = client.get("/api/sessions/1/positions")
        assert response.status_code == 404
        assert response.json == {"error": "Session not found"}


def test_get_sessions_internal_error(client):
    """
    Tests the /sessions endpoint for internal server error.
    """
    with patch(
        "routes.sessions.session_service.get_all_sessions"
    ) as mock_get_all_sessions:
        mock_get_all_sessions.side_effect = Exception("Internal Error")
        response = client.get("/api/sessions")
        assert response.status_code == 500
        assert response.json == {"error": "An internal error occurred"}
