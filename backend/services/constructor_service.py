from models import ConstructorStats


def get_constructors_by_year(year, team_name=None):
    """
    Retrieves constructor stats for a given year,
    optionally filtered by team name.
    """
    if not year:
        raise ValueError("Year parameter is required")

    query = ConstructorStats.query.filter_by(year=year)

    if team_name:
        query = query.filter_by(team_name=team_name)

    constructors = query.order_by(ConstructorStats.position).all()

    return [c.to_dict() for c in constructors]


def get_constructor_details(year, team_name):
    """
    Retrieves detailed stats for a specific constructor in a given year.
    """
    if not year or not team_name:
        raise ValueError("Year and team_name parameters are required")

    constructor = ConstructorStats.query.filter_by(
        team_name=team_name, year=year
    ).first()

    return constructor.to_dict() if constructor else None


def get_constructor_standings_by_year(year):
    """
    Retrieves constructor standings for a given year, ordered by position.
    """
    if not year:
        raise ValueError("Year parameter is required")

    standings = (
        ConstructorStats.query.filter_by(year=year)
        .order_by(ConstructorStats.position)
        .all()
    )

    return [standing.to_dict() for standing in standings]
