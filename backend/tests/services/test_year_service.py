from services import year_service
from datetime import datetime


def test_get_available_years_with_details(mocker, app):
    """
    Tests that the get_available_years_with_details function returns a list of
    years with their details.
    """
    with app.app_context():
        mock_year_data = mocker.MagicMock()
        mock_year_data.year = 2023
        mock_year_data.last_synced = datetime(2023, 1, 1)
        mock_year_data.drivers_count = 20
        mock_year_data.sessions_count = 22

        # Patch the YearData that's imported into the year_service module
        mock_patch = mocker.patch.object(year_service, "YearData")
        mock_patch.query.all.return_value = [mock_year_data]

        years_data = year_service.get_available_years_with_details()

        assert len(years_data) == 8  # 2018 to 2025

        synced_year = next((y for y in years_data if y["year"] == 2023), None)
        assert synced_year is not None
        assert synced_year["synced"] is True
        assert synced_year["last_synced"] == "2023-01-01T00:00:00"
        assert synced_year["drivers_count"] == 20
        assert synced_year["sessions_count"] == 22

        unsynced_year = next((y for y in years_data if y["year"] == 2024), None)
        assert unsynced_year is not None
        assert unsynced_year["synced"] is False
        assert unsynced_year["last_synced"] is None
        assert unsynced_year["drivers_count"] == 0
        assert unsynced_year["sessions_count"] == 0


def test_get_available_years_with_no_synced_data(mocker, app):
    """
    Tests that the get_available_years_with_details function returns all years
    as unsynced when there is no data in the database.
    """
    with app.app_context():
        # Patch the YearData that's imported into the year_service module
        mock_patch = mocker.patch.object(year_service, "YearData")
        mock_patch.query.all.return_value = []

        years_data = year_service.get_available_years_with_details()

        assert len(years_data) == 8
        for year in years_data:
            assert year["synced"] is False
            assert year["last_synced"] is None
            assert year["drivers_count"] == 0
            assert year["sessions_count"] == 0
