from unittest.mock import patch


def test_get_drivers(client):
    """
    Tests the /drivers endpoint.
    """
    with patch(
        "routes.drivers.driver_service.get_driver_stats"
    ) as mock_get_driver_stats:
        mock_get_driver_stats.return_value = [{"name": "Test Driver"}]
        response = client.get("/api/drivers?year=2023")
        assert response.status_code == 200
        assert response.json == [{"name": "Test Driver"}]
        mock_get_driver_stats.assert_called_once_with(2023, None)


def test_get_drivers_not_found(client):
    """
    Tests the /drivers endpoint when no drivers are found.
    """
    with patch(
        "routes.drivers.driver_service.get_driver_stats"
    ) as mock_get_driver_stats:
        mock_get_driver_stats.return_value = []
        response = client.get("/api/drivers?year=2023")
        assert response.status_code == 404
        assert response.json == {"error": "No drivers found for the given criteria"}


def test_get_driver_sessions(client):
    """
    Tests the /drivers/sessions endpoint.
    """
    with patch(
        "routes.drivers.driver_service.get_driver_session_stats"
    ) as mock_get_driver_session_stats:
        mock_get_driver_session_stats.return_value = [{"name": "Test Session"}]
        response = client.get("/api/drivers/sessions?year=2023&driver_number=44")
        assert response.status_code == 200
        assert response.json == [{"name": "Test Session"}]
        mock_get_driver_session_stats.assert_called_once_with(2023, 44)


def test_get_driver_sessions_not_found(client):
    """
    Tests the /drivers/sessions endpoint when no sessions are found.
    """
    with patch(
        "routes.drivers.driver_service.get_driver_session_stats"
    ) as mock_get_driver_session_stats:
        mock_get_driver_session_stats.return_value = []
        response = client.get("/api/drivers/sessions?year=2023&driver_number=44")
        assert response.status_code == 404
        assert response.json == {
            "error": "No session data found for the given criteria"
        }


def test_get_drivers_value_error(client):
    """
    Tests the /drivers endpoint for ValueError.
    """
    with patch(
        "routes.drivers.driver_service.get_driver_stats"
    ) as mock_get_driver_stats:
        mock_get_driver_stats.side_effect = ValueError("Invalid year")
        response = client.get("/api/drivers?year=abc")
        assert response.status_code == 400
        assert response.json == {"error": "Invalid year"}
