import pytest
from services import constructor_service


def test_get_constructors_by_year(mocker, app):
    """
    Tests that the get_constructors_by_year function returns a list of
    constructor stats.
    """
    with app.app_context():
        mock_constructor_stats = mocker.MagicMock()
        mock_constructor_stats.to_dict.return_value = {
            "team_name": "Mercedes",
            "position": 1,
        }
        mock_query = mocker.patch("services.constructor_service.ConstructorStats.query")
        mock_query.filter_by.return_value.order_by.return_value.all.return_value = [
            mock_constructor_stats
        ]

        stats = constructor_service.get_constructors_by_year(year=2023)

        assert stats == [{"team_name": "Mercedes", "position": 1}]
        mock_query.filter_by.assert_called_once_with(year=2023)


def test_get_constructors_by_year_with_team_name(mocker, app):
    """
    Tests that the get_constructors_by_year function returns a list of
    constructor stats for a specific team.
    """
    with app.app_context():
        mock_constructor_stats = mocker.MagicMock()
        mock_constructor_stats.to_dict.return_value = {
            "team_name": "Mercedes",
            "position": 1,
        }
        mock_query = mocker.patch("services.constructor_service.ConstructorStats.query")
        mock_chain = mock_query.filter_by.return_value.filter_by.return_value
        mock_chain.order_by.return_value.all.return_value = [mock_constructor_stats]

        stats = constructor_service.get_constructors_by_year(
            year=2023, team_name="Mercedes"
        )

        assert stats == [{"team_name": "Mercedes", "position": 1}]
        mock_query.filter_by.assert_any_call(year=2023)
        mock_query.filter_by.return_value.filter_by.assert_called_once_with(
            team_name="Mercedes"
        )


def test_get_constructors_by_year_no_year():
    """
    Tests that the get_constructors_by_year function raises a ValueError
    when no year is provided.
    """
    with pytest.raises(ValueError, match="Year parameter is required"):
        constructor_service.get_constructors_by_year(year=None)


def test_get_constructor_details(mocker, app):
    """
    Tests that the get_constructor_details function returns detailed stats
    for a constructor.
    """
    with app.app_context():
        mock_constructor_stats = mocker.MagicMock()
        mock_constructor_stats.to_dict.return_value = {
            "team_name": "Mercedes",
            "position": 1,
        }
        mock_query = mocker.patch("services.constructor_service.ConstructorStats.query")
        mock_query.filter_by.return_value.first.return_value = mock_constructor_stats

        details = constructor_service.get_constructor_details(
            year=2023, team_name="Mercedes"
        )

        assert details == {"team_name": "Mercedes", "position": 1}
        mock_query.filter_by.assert_called_once_with(team_name="Mercedes", year=2023)


def test_get_constructor_details_no_params():
    """
    Tests that the get_constructor_details function raises a ValueError
    when year or team_name are not provided.
    """
    error_msg = "Year and team_name parameters are required"
    with pytest.raises(ValueError, match=error_msg):
        constructor_service.get_constructor_details(year=None, team_name=None)
    with pytest.raises(ValueError, match=error_msg):
        constructor_service.get_constructor_details(year=2023, team_name=None)
    with pytest.raises(ValueError, match=error_msg):
        constructor_service.get_constructor_details(year=None, team_name="Mercedes")


def test_get_constructor_standings_by_year(mocker, app):
    """
    Tests that the get_constructor_standings_by_year function returns a list
    of constructor standings.
    """
    with app.app_context():
        mock_constructor_stats = mocker.MagicMock()
        mock_constructor_stats.to_dict.return_value = {
            "team_name": "Mercedes",
            "position": 1,
        }
        mock_query = mocker.patch("services.constructor_service.ConstructorStats.query")
        mock_query.filter_by.return_value.order_by.return_value.all.return_value = [
            mock_constructor_stats
        ]

        standings = constructor_service.get_constructor_standings_by_year(year=2023)

        assert standings == [{"team_name": "Mercedes", "position": 1}]
        mock_query.filter_by.assert_called_once_with(year=2023)


def test_get_constructor_standings_by_year_no_year():
    """
    Tests that the get_constructor_standings_by_year function raises a
    ValueError when no year is provided.
    """
    with pytest.raises(ValueError, match="Year parameter is required"):
        constructor_service.get_constructor_standings_by_year(year=None)
