from models import YearData


def get_available_years_with_details():
    """
    Generates a list of years from 2018 to 2025 with their sync status
    and other details from the database. This date range is arbitrary
    and can be changed if needed. Currently only 2025 data is available.
    """
    all_year_data = YearData.query.all()
    synced_years = {
        int(yd.year): yd for yd in all_year_data if hasattr(yd, "year") and yd.year
    }
    years_data = []

    for year in range(2018, 2026):
        year_info = {"year": year, "synced": year in synced_years}
        if year in synced_years:
            synced_year = synced_years[year]
            last_synced = synced_year.last_synced
            year_info["last_synced"] = last_synced.isoformat() if last_synced else None
            year_info["drivers_count"] = synced_year.drivers_count
            year_info["sessions_count"] = synced_year.sessions_count
        else:
            year_info["last_synced"] = None
            year_info["drivers_count"] = 0
            year_info["sessions_count"] = 0
        years_data.append(year_info)

    return years_data
