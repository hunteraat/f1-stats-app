import pytest
from services import driver_service


def test_get_driver_stats(mocker, app):
    """
    Tests that the get_driver_stats function returns a list of driver stats.
    """
    with app.app_context():
        mock_driver_stats = mocker.MagicMock()
        mock_driver_stats.to_dict.return_value = {"driver_number": 44, "position": 1}
        mock_query = mocker.patch("services.driver_service.DriverStats.query")
        mock_query.filter_by.return_value.order_by.return_value.all.return_value = [
            mock_driver_stats
        ]

        stats = driver_service.get_driver_stats(year=2023)

        assert stats == [{"driver_number": 44, "position": 1}]
        mock_query.filter_by.assert_called_once_with(year=2023)


def test_get_driver_stats_with_driver_number(mocker, app):
    """
    Tests that the get_driver_stats function returns a list of driver stats
    for a specific driver.
    """
    with app.app_context():
        mock_driver_stats = mocker.MagicMock()
        mock_driver_stats.to_dict.return_value = {"driver_number": 44, "position": 1}
        mock_query = mocker.patch("services.driver_service.DriverStats.query")
        mock_chain = mock_query.filter_by.return_value.filter_by.return_value
        mock_chain.order_by.return_value.all.return_value = [mock_driver_stats]

        stats = driver_service.get_driver_stats(year=2023, driver_number=44)

        assert stats == [{"driver_number": 44, "position": 1}]
        mock_query.filter_by.assert_any_call(year=2023)
        mock_query.filter_by.return_value.filter_by.assert_called_once_with(
            driver_number=44
        )


def test_get_driver_stats_no_year():
    """
    Tests that the get_driver_stats function raises a ValueError when no year
    is provided.
    """
    with pytest.raises(ValueError, match="Year parameter is required"):
        driver_service.get_driver_stats(year=None)


def test_get_driver_session_stats(mocker, app):
    """
    Tests that the get_driver_session_stats function returns a list of session
    stats for a driver.
    """
    with app.app_context():
        mock_session_stats = mocker.MagicMock()
        mock_session_stats.to_dict.return_value = {
            "session_name": "Test GP",
            "position": 1,
        }
        mock_query = mocker.patch("services.driver_service.DriverSessionStats.query")
        mock_query.filter_by.return_value.order_by.return_value.all.return_value = [
            mock_session_stats
        ]

        stats = driver_service.get_driver_session_stats(year=2023, driver_number=44)

        assert stats == [{"session_name": "Test GP", "position": 1}]
        mock_query.filter_by.assert_called_once_with(driver_number=44, year=2023)


def test_get_driver_session_stats_no_params():
    """
    Tests that the get_driver_session_stats function raises a ValueError
    when year or driver_number are not provided.
    """
    error_msg = "Year and driver_number parameters are required"
    with pytest.raises(ValueError, match=error_msg):
        driver_service.get_driver_session_stats(year=None, driver_number=None)
    with pytest.raises(ValueError, match=error_msg):
        driver_service.get_driver_session_stats(year=2023, driver_number=None)
    with pytest.raises(ValueError, match=error_msg):
        driver_service.get_driver_session_stats(year=None, driver_number=44)
