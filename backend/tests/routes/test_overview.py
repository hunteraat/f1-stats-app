from unittest.mock import patch


def test_get_stats_summary(client):
    """
    Tests the /overview endpoint.
    """
    with patch(
        "routes.overview.overview_service.get_stats_summary"
    ) as mock_get_summary:
        mock_get_summary.return_value = {"total_drivers": 10}
        response = client.get("/api/overview")
        assert response.status_code == 200
        assert response.json == {"total_drivers": 10}
        mock_get_summary.assert_called_once_with(None)


def test_get_stats_summary_with_year(client):
    """
    Tests the /overview endpoint with a year filter.
    """
    with patch(
        "routes.overview.overview_service.get_stats_summary"
    ) as mock_get_summary:
        mock_get_summary.return_value = {"total_drivers": 5}
        response = client.get("/api/overview?year=2023")
        assert response.status_code == 200
        assert response.json == {"total_drivers": 5}
        mock_get_summary.assert_called_once_with(2023)


def test_get_stats_summary_internal_error(client):
    """
    Tests the /overview endpoint for internal server error.
    """
    with patch(
        "routes.overview.overview_service.get_stats_summary"
    ) as mock_get_summary:
        mock_get_summary.side_effect = Exception("Internal Error")
        response = client.get("/api/overview")
        assert response.status_code == 500
        assert response.json == {"error": "An internal error occurred"}
