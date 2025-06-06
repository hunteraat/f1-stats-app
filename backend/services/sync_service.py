import asyncio
from datetime import datetime, timezone

import aiohttp
from dateutil.relativedelta import relativedelta
from flask import current_app

from extensions import db
from models import (
    Driver,
    Session,
    DriverSession,
    Position,
    Lap,
    YearData,
)


def make_aware(dt):
    """Convert naive datetime to UTC aware datetime"""
    if dt and dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def fetch_data_async(session, endpoint, params, max_retries=3, initial_delay=1):
    """Fetch data asynchronously with retries for rate limiting"""
    url = f"https://api.openf1.org/v1/{endpoint}"
    retry_count = 0
    delay = initial_delay
    logger = current_app.logger

    while retry_count <= max_retries:
        try:
            logger.info(f"Requesting: {url} with params: {params}")
            async with session.get(url, params=params) as response:
                status = response.status
                if status == 200:
                    return await response.json()
                elif status == 429:
                    if retry_count < max_retries:
                        logger.warning(f"Rate limited. Retrying in {delay}s.")
                        await asyncio.sleep(delay)
                        delay *= 2
                        retry_count += 1
                    else:
                        logger.error("Max retries reached after rate limit.")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(f"HTTP Error {status}: {error_text}")
                    return None
        except aiohttp.ClientError as e:
            logger.error(f"ClientError during request: {e}")
            if retry_count < max_retries:
                await asyncio.sleep(delay)
                delay *= 2
                retry_count += 1
            else:
                logger.error("Max retries reached after client error.")
                return None
    return None


async def run_sync_for_year(year):
    """Orchestrates the data synchronization for a given year."""
    logger = current_app.logger
    year_data = YearData.query.filter_by(year=year).first()
    if not year_data:
        year_data = YearData(year=year)
        db.session.add(year_data)
        db.session.commit()

    if year_data.sync_status == "in_progress":
        raise Exception("Sync for this year is already in progress.")

    year_data.sync_status = "in_progress"
    year_data.sync_message = "Starting sync..."
    db.session.commit()

    try:
        await _fetch_and_process_data(year, year_data)

        year_data.sync_status = "completed"
        year_data.sync_message = "Sync completed successfully."
        year_data.last_synced = datetime.utcnow()
        year_data.last_incremental_sync = datetime.utcnow()
        db.session.commit()
        logger.info(f"Sync for year {year} completed successfully.")
        return {"success": True, "message": f"Sync for {year} completed."}

    except Exception as e:
        db.session.rollback()
        logger.error(f"Sync for {year} failed: {e}", exc_info=True)
        year_data.sync_status = "error"
        year_data.sync_message = str(e)
        db.session.commit()
        raise e


async def _fetch_and_process_data(year, year_data):
    """Handles the core data fetching and processing logic."""
    logger = current_app.logger
    logger.info("Initializing sync...")

    async with aiohttp.ClientSession() as session:
        sessions_data = await _get_sessions_data(session, year, year_data)
        if not sessions_data:
            raise Exception(f"No sessions found for year {year}")

        drivers_data = await _get_drivers_data(session, year, sessions_data)
        if not drivers_data:
            raise Exception(f"No drivers found for year {year}")

        logger.info("Processing drivers...")
        _process_drivers(drivers_data)

        logger.info("Processing sessions...")
        _process_sessions(sessions_data, year)

        _process_driver_sessions(drivers_data)

        logger.info("Processing positions and laps...")
        await _process_positions_and_laps(session, year, year_data)


async def _get_sessions_data(session, year, year_data):
    """Fetches session data from cache or API."""
    logger = current_app.logger

    logger.info("Fetching sessions from API...")
    sessions_data = await fetch_data_async(session, "sessions", {"year": year})
    if not sessions_data:
        return None

    return sessions_data


async def _get_drivers_data(session, year, sessions_data):
    """Fetches driver data for all sessions in a year."""
    logger = current_app.logger
    logger.info("Fetching drivers for each session...")
    session_keys = [s["session_key"] for s in sessions_data]
    tasks = [
        fetch_data_async(session, "drivers", {"session_key": key})
        for key in session_keys
    ]
    results = await asyncio.gather(*tasks)
    return [item for sublist in results if sublist for item in sublist]


def _process_drivers(drivers_data):
    """Upserts driver information into the database."""
    unique_drivers_data = {}
    for d in drivers_data:
        driver_number = d.get("driver_number")
        if not driver_number:
            continue
        if driver_number not in unique_drivers_data:
            unique_drivers_data[driver_number] = {"driver_number": driver_number}

        for key in [
            "full_name",
            "team_name",
            "team_colour",
            "country_code",
            "headshot_url",
        ]:
            if d.get(key) is not None:
                unique_drivers_data[driver_number][key] = d.get(key)

    for driver_data in unique_drivers_data.values():
        driver = Driver.query.filter_by(
            driver_number=driver_data["driver_number"]
        ).first()
        if not driver:
            driver = Driver(driver_number=driver_data["driver_number"])
            db.session.add(driver)
        driver.full_name = driver_data.get("full_name")
        driver.team_name = driver_data.get("team_name")
        driver.team_colour = driver_data.get("team_colour")
        driver.country_code = driver_data.get("country_code")
        driver.headshot_url = driver_data.get("headshot_url")
    db.session.commit()


def _process_sessions(sessions_data, year):
    """Upserts session information into the database."""
    for session_data in sessions_data:
        session = Session.query.filter_by(
            session_key=session_data["session_key"]
        ).first()
        if not session:
            session = Session(session_key=session_data["session_key"])
            db.session.add(session)
        date_start = session_data.get("date_start")
        session.session_name = session_data.get("session_name")
        session.date_start = (
            make_aware(datetime.fromisoformat(date_start.replace("Z", "+00:00")))
            if date_start
            else None
        )
        session.session_type = session_data.get("session_type")
        session.meeting_key = session_data.get("meeting_key")
        session.location = session_data.get("location")
        session.year = year
    db.session.commit()


def _process_driver_sessions(drivers_data):
    """Creates driver_session records from driver data."""
    logger = current_app.logger
    logger.info("Processing driver sessions...")

    driver_numbers = {
        d.get("driver_number") for d in drivers_data if d.get("driver_number")
    }
    session_keys = {d.get("session_key") for d in drivers_data if d.get("session_key")}

    if not driver_numbers or not session_keys:
        logger.info("No driver numbers or session keys found in data to process.")
        return

    drivers = Driver.query.filter(Driver.driver_number.in_(driver_numbers)).all()
    driver_map = {d.driver_number: d.id for d in drivers}

    sessions = Session.query.filter(Session.session_key.in_(session_keys)).all()
    session_map = {s.session_key: s.id for s in sessions}

    processed_pairs = set()

    for data in drivers_data:
        driver_number = data.get("driver_number")
        session_key = data.get("session_key")

        if not driver_number or not session_key:
            continue

        pair = (driver_number, session_key)
        if pair in processed_pairs:
            continue
        processed_pairs.add(pair)

        driver_id = driver_map.get(driver_number)
        session_id = session_map.get(session_key)

        if not driver_id:
            logger.warning(f"Driver {driver_number} not found in database.")
            continue
        if not session_id:
            logger.warning(f"Session {session_key} not found in database.")
            continue

        # Check if DriverSession already exists to avoid duplicates
        existing = DriverSession.query.filter_by(
            driver_id=driver_id, session_id=session_id
        ).first()

        if not existing:
            driver_session = DriverSession(driver_id=driver_id, session_id=session_id)
            db.session.add(driver_session)

    db.session.commit()


async def _process_positions_and_laps(session, year, year_data):
    """Fetches and processes position and lap data for a given year."""
    logger = current_app.logger
    is_current_year = year == datetime.now(timezone.utc).year

    # Determine the date range for fetching data
    if is_current_year and year_data.last_incremental_sync:
        # For incremental sync, start from the last sync time
        start_date_dt = make_aware(year_data.last_incremental_sync)
        logger.info(f"Performing incremental sync from {start_date_dt.isoformat()}")
    else:
        # For full sync, start from beginning of year
        start_date_dt = datetime(year, 1, 1, tzinfo=timezone.utc)
        logger.info(f"Performing full sync for {year}")

    end_date_dt = (
        datetime.now(timezone.utc)
        if is_current_year
        else datetime(year, 12, 31, 23, 59, 59, tzinfo=timezone.utc)
    )

    start_date, end_date = start_date_dt.isoformat(), end_date_dt.isoformat()

    # Fetch position and lap data
    pos_task = fetch_data_by_month(session, "position", start_date, end_date, "date")
    lap_task = fetch_data_by_month(session, "laps", start_date, end_date, "date_start")
    positions_data, laps_data = await asyncio.gather(pos_task, lap_task)

    if positions_data:
        logger.info(f"Processing {len(positions_data)} position records...")
        _process_positions_batch(positions_data)

    if laps_data:
        logger.info(f"Processing {len(laps_data)} lap records...")
        _process_laps_batch(laps_data)

    # Update the last incremental sync time for current year
    if is_current_year:
        year_data.last_incremental_sync = datetime.utcnow()

    db.session.commit()


def _get_driver_session_id(cache, session_key, driver_number):
    """Helper to get driver_session_id from cache or DB."""
    cache_key = (session_key, driver_number)
    if cache_key in cache:
        return cache[cache_key]

    driver_session_id = (
        db.session.query(DriverSession.id)
        .join(Session)
        .join(Driver)
        .filter(
            Session.session_key == session_key,
            Driver.driver_number == driver_number,
        )
        .scalar()
    )
    if driver_session_id:
        cache[cache_key] = driver_session_id
    return driver_session_id


def _process_positions_batch(positions_data):
    """Processes a batch of position data."""
    logger = current_app.logger
    cache = {}
    for pos in positions_data:
        session_key = pos.get("session_key")
        driver_number = pos.get("driver_number")
        if not session_key or not driver_number:
            continue

        driver_session_id = _get_driver_session_id(cache, session_key, driver_number)
        if not driver_session_id:
            logger.warning(
                f"Could not find driver_session for {session_key}, " f"{driver_number}"
            )
            continue

        date = make_aware(datetime.fromisoformat(pos["date"].replace("Z", "+00:00")))

        # Check if position already exists to avoid duplicates in incremental sync
        existing_position = Position.query.filter_by(
            driver_session_id=driver_session_id, date=date, position=pos["position"]
        ).first()

        if not existing_position:
            position = Position(
                driver_session_id=driver_session_id,
                date=date,
                position=pos["position"],
            )
            db.session.add(position)
    db.session.commit()


def _process_laps_batch(laps_data):
    """Processes a batch of lap data."""
    logger = current_app.logger
    cache = {}
    for lap in laps_data:
        if not lap.get("lap_duration"):
            continue

        session_key = lap.get("session_key")
        driver_number = lap.get("driver_number")
        if not session_key or not driver_number:
            continue

        driver_session_id = _get_driver_session_id(cache, session_key, driver_number)
        if not driver_session_id:
            logger.warning(
                f"Could not find driver_session for {session_key}, " f"{driver_number}"
            )
            continue

        # Check if lap already exists to avoid duplicates in incremental sync
        existing_lap = Lap.query.filter_by(
            driver_session_id=driver_session_id, lap_number=lap.get("lap_number", 0)
        ).first()

        if not existing_lap:
            new_lap = Lap(
                driver_session_id=driver_session_id,
                lap_number=lap.get("lap_number", 0),
                lap_time=lap.get("lap_duration"),
            )
            db.session.add(new_lap)
    db.session.commit()


async def fetch_data_by_month(
    session, endpoint, start_date, end_date, param_name="date"
):
    """Fetch data month by month to handle large datasets"""
    all_data = []
    current_date = make_aware(datetime.fromisoformat(start_date.replace("Z", "+00:00")))
    final_date = make_aware(datetime.fromisoformat(end_date.replace("Z", "+00:00")))

    while current_date < final_date:
        next_date = current_date + relativedelta(months=1)
        if next_date > final_date:
            next_date = final_date

        params = {
            f"{param_name}>": current_date.isoformat(),
            f"{param_name}<": next_date.isoformat(),
        }

        month_str = current_date.strftime("%Y-%m")
        current_app.logger.info(f"Fetching {endpoint} for {month_str}")
        month_data = await fetch_data_async(session, endpoint, params)
        if month_data:
            all_data.extend(month_data)
        current_date = next_date
        await asyncio.sleep(0.5)

    return all_data
