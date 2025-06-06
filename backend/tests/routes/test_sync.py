import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock


@pytest.mark.asyncio
async def test_sync_f1_data_route(client):
    """
    Tests the /sync/data/<year> endpoint.
    """
    with patch(
        "routes.sync.run_sync_for_year", new_callable=AsyncMock
    ) as mock_run_sync:
        mock_run_sync.return_value = {"status": "success"}

        # Run the client call in a separate thread to avoid event loop conflicts
        response = await asyncio.to_thread(client.post, "/api/sync/data/2023")

        assert response.status_code == 200
        assert response.json == {"status": "success"}
        mock_run_sync.assert_called_once_with(2023)


def test_get_sync_status(client):
    """
    Tests the /sync/status/<year> endpoint.
    """
    with patch("routes.sync.YearData.query") as mock_query:
        mock_year_data = MagicMock()
        mock_year_data.to_dict.return_value = {"status": "completed"}
        mock_query.filter_by.return_value.first.return_value = mock_year_data
        response = client.get("/api/sync/status/2023")
        assert response.status_code == 200
        assert response.json == {"status": "completed"}
        mock_query.filter_by.assert_called_once_with(year=2023)


def test_reset_database(client):
    """
    Tests the /sync/database/reset endpoint.
    """
    with patch("routes.sync.db.drop_all") as mock_drop_all, patch(
        "routes.sync.db.create_all"
    ) as mock_create_all:
        response = client.post("/api/sync/database/reset")
        assert response.status_code == 200
        assert response.json == {
            "success": True,
            "message": "Database reset successfully.",
        }
        mock_drop_all.assert_called_once()
        mock_create_all.assert_called_once()


def test_clear_lap_data(client):
    """
    Tests the /sync/data/<year>/clear-laps endpoint.
    """
    with patch("routes.sync.db.session.commit"), patch(
        "routes.sync.Lap.query"
    ) as mock_lap_query, patch(
        "routes.sync.Session.query"
    ) as mock_session_query, patch(
        "routes.sync.DriverSession.query"
    ) as mock_driver_session_query:

        mock_session_query.filter_by.return_value.all.return_value = [MagicMock(id=1)]
        mock_driver_session_query.filter.return_value.all.return_value = [
            MagicMock(id=1)
        ]
        mock_lap_query.filter.return_value.delete.return_value = 5

        response = client.post("/api/sync/data/2023/clear-laps")
        assert response.status_code == 200
        assert response.json["success"]
        assert response.json["message"] == "Successfully deleted 5 lap records for 2023"
