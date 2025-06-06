from unittest.mock import patch


def test_get_available_years(client):
    """
    Tests the /years endpoint.
    """
    with patch(
        "routes.years.year_service.get_available_years_with_details"
    ) as mock_get_years:
        mock_get_years.return_value = [{"year": 2023, "synced": True}]
        response = client.get("/api/years")
        assert response.status_code == 200
        assert response.json == [{"year": 2023, "synced": True}]
        mock_get_years.assert_called_once()


def test_get_available_years_internal_error(client):
    """
    Tests the /years endpoint for internal server error.
    """
    with patch(
        "routes.years.year_service.get_available_years_with_details"
    ) as mock_get_years:
        mock_get_years.side_effect = Exception("Internal Error")
        response = client.get("/api/years")
        assert response.status_code == 500
        assert response.json == {"error": "An internal error occurred"}
