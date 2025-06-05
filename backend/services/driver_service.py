from models import DriverStats, DriverSessionStats


def get_driver_stats(year, driver_number=None):
    """
    Retrieves driver statistics for a given year,
    optionally filtered by driver number.
    """
    if not year:
        raise ValueError("Year parameter is required")

    query = DriverStats.query.filter_by(year=year)

    if driver_number:
        query = query.filter_by(driver_number=driver_number)

    drivers = query.order_by(DriverStats.position).all()
    return [d.to_dict() for d in drivers]


def get_driver_session_stats(year, driver_number):
    """
    Retrieves all session statistics for a given driver and year.
    """
    if not year or not driver_number:
        raise ValueError("Year and driver_number parameters are required")

    sessions = (
        DriverSessionStats.query.filter_by(driver_number=driver_number, year=year)
        .order_by(DriverSessionStats.date_start.desc())
        .all()
    )
    return [s.to_dict() for s in sessions]
