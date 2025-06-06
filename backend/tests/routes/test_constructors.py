from unittest.mock import patch


def test_get_constructors(client):
    """
    Tests the /constructors endpoint.
    """
    with patch(
        "routes.constructors.constructor_service.get_constructors_by_year"
    ) as mock_get_constructors:
        mock_get_constructors.return_value = [{"name": "Test Constructor"}]
        response = client.get("/api/constructors?year=2023")
        assert response.status_code == 200
        assert response.json == [{"name": "Test Constructor"}]
        mock_get_constructors.assert_called_once_with(2023, None)


def test_get_constructor(client):
    """
    Tests the /constructors/<team_name> endpoint.
    """
    with patch(
        "routes.constructors.constructor_service.get_constructor_details"
    ) as mock_get_details:
        mock_get_details.return_value = {"name": "Test Constructor"}
        response = client.get("/api/constructors/Test%20Constructor?year=2023")
        assert response.status_code == 200
        assert response.json == {"name": "Test Constructor"}
        mock_get_details.assert_called_once_with(2023, "Test Constructor")


def test_get_constructor_standings(client):
    """
    Tests the /constructors/<year> endpoint.
    """
    with patch(
        "routes.constructors.constructor_service.get_constructor_standings_by_year"
    ) as mock_get_standings:
        mock_get_standings.return_value = [{"name": "Test Constructor"}]
        response = client.get("/api/constructors/2023")
        assert response.status_code == 200
        assert response.json == [{"name": "Test Constructor"}]
        mock_get_standings.assert_called_once_with(2023)


def test_get_constructors_not_found(client):
    """
    Tests the /constructors endpoint for a 404 case.
    """
    with patch(
        "routes.constructors.constructor_service.get_constructors_by_year"
    ) as mock_get_constructors:
        mock_get_constructors.return_value = []
        response = client.get("/api/constructors?year=2023")
        assert response.status_code == 404
        assert response.json == {"error": "No data found for the given criteria"}
