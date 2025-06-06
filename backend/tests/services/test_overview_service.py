from services import overview_service
from models import Session
from datetime import datetime


def test_get_stats_summary(mocker, app):
    """
    Tests that the get_stats_summary function returns a summary of stats.
    """
    with app.app_context():
        mock_driver_query = mocker.patch("services.overview_service.Driver.query")
        mock_driver_query.count.return_value = 10

        mock_session_query = mocker.patch("services.overview_service.Session.query")
        mock_session_query.count.return_value = 20

        mock_latest_session = mocker.MagicMock(spec=Session)
        mock_latest_session.session_name = "Test Grand Prix"
        mock_latest_session.location = "Test Location"
        mock_latest_session.date_start = datetime(2023, 1, 1)
        mock_query_chain = mock_session_query.order_by.return_value
        mock_query_chain.first.return_value = mock_latest_session

        mock_active_drivers_query = mocker.patch(
            "services.overview_service.db.session.query"
        )
        mock_active_chain = mock_active_drivers_query.return_value.join.return_value
        mock_active_chain.distinct.return_value.count.return_value = 5

        summary = overview_service.get_stats_summary()

        assert summary["total_drivers"] == 10
        assert summary["total_sessions"] == 20
        assert summary["active_drivers"] == 5
        assert summary["latest_session"]["name"] == "Test Grand Prix"
        assert summary["year"] is None


def test_get_stats_summary_with_year(mocker, app):
    """
    Tests that the get_stats_summary function returns a summary of stats
    for a specific year.
    """
    with app.app_context():
        mock_drivers_query = mocker.patch("services.overview_service.db.session.query")
        mock_driver_chain = mock_drivers_query.return_value.join.return_value
        mock_driver_chain = mock_driver_chain.join.return_value.filter.return_value
        mock_driver_chain.distinct.return_value.count.return_value = 2

        mock_session_query = mocker.patch("services.overview_service.Session.query")
        mock_session_query.filter.return_value.count.return_value = 5

        mock_latest_session = mocker.MagicMock(spec=Session)
        mock_latest_session.session_name = "Test Grand Prix 2023"
        mock_latest_session.location = "Test Location 2023"
        mock_latest_session.date_start = datetime(2023, 1, 1)
        mock_session_chain = mock_session_query.filter.return_value
        mock_session_chain.order_by.return_value.first.return_value = (
            mock_latest_session
        )

        summary = overview_service.get_stats_summary(year=2023)

        assert summary["total_drivers"] == 2
        assert summary["total_sessions"] == 5
        assert summary["active_drivers"] == 2
        assert summary["latest_session"]["name"] == "Test Grand Prix 2023"
        assert summary["year"] == 2023


def test_get_stats_summary_no_latest_session(mocker, app):
    """
    Tests that the get_stats_summary function handles the case where there is
    no latest session.
    """
    with app.app_context():
        mock_driver_query = mocker.patch("services.overview_service.Driver.query")
        mock_driver_query.count.return_value = 0

        mock_session_query = mocker.patch("services.overview_service.Session.query")
        mock_session_query.count.return_value = 0
        mock_session_query.order_by.return_value.first.return_value = None

        mock_active_drivers_query = mocker.patch(
            "services.overview_service.db.session.query"
        )
        mock_active_chain = mock_active_drivers_query.return_value.join.return_value
        mock_active_chain.distinct.return_value.count.return_value = 0

        summary = overview_service.get_stats_summary()

        assert summary["total_drivers"] == 0
        assert summary["total_sessions"] == 0
        assert summary["active_drivers"] == 0
        assert summary["latest_session"] is None
        assert summary["year"] is None
