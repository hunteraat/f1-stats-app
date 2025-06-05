from flask import jsonify, current_app
from datetime import datetime, timedelta, timezone
from models import (
    Driver,
    Session,
    DriverSession,
    Position,
    Lap,
    YearData,
    SessionKeyCache,
)
from extensions import db
from utils import fetch_f1_data, add_cors_headers
import asyncio
import aiohttp
import json
from dateutil.relativedelta import relativedelta
import logging
from . import sync_bp

sync_bp = add_cors_headers(sync_bp)


def make_aware(dt):
    """Convert naive datetime to UTC aware datetime"""
    if dt.tzinfo is None:
        return dt.replace(tzinfo=timezone.utc)
    return dt


async def fetch_data_async(
    session, endpoint, params, max_retries=3, initial_delay=1
):
    """Fetch data asynchronously with retries for rate limiting"""
    url = f"https://api.openf1.org/v1/{endpoint}"
    retry_count = 0
    delay = initial_delay
    logger = current_app.logger

    while retry_count <= max_retries:
        try:
            logger.info(f"Making request to: {url}")
            logger.debug(f"With params: {params}")

            async with session.get(url, params=params) as response:
                status = response.status
                logger.info(f"Response status: {status}")

                if status == 200:
                    data = await response.json()
                    logger.info(
                        f"Received {len(data) if data else 0} "
                        f"records for {endpoint}"
                    )
                    return data
                elif status == 429:  # Rate limited
                    if retry_count < max_retries:
                        logger.warning(
                            f"Rate limited on {endpoint}. Retrying in {delay}s..."
                        )
                        await asyncio.sleep(delay)
                        delay *= 2  # Exponential backoff
                        retry_count += 1
                        continue
                    else:
                        logger.error(f"Max retries for {endpoint} after rate limit")
                        return None
                else:
                    error_text = await response.text()
                    logger.error(
                        f"Error for {endpoint}: Status {status}\n{error_text}"
                    )
                    return None

        except aiohttp.ClientError as e:
            logger.error(f"Exception during {endpoint} request: {e}")
            if retry_count < max_retries:
                logger.info(f"Retrying in {delay} seconds...")
                await asyncio.sleep(delay)
                delay *= 2
                retry_count += 1
                continue
            return None

    return None


async def fetch_data_by_month(
    session, endpoint, start_date, end_date, param_name="date"
):
    """Fetch data month by month to handle large datasets"""
    all_data = []
    current_date = make_aware(datetime.fromisoformat(start_date.replace("Z", "+00:00")))
    final_date = make_aware(datetime.fromisoformat(end_date.replace("Z", "+00:00")))
    logger = current_app.logger

    while current_date < final_date:
        next_date = current_date + relativedelta(months=1)
        if next_date > final_date:
            next_date = final_date

        params = {
            f"{param_name}>": current_date.isoformat(),
            f"{param_name}<": next_date.isoformat(),
        }

        logger.info(f"Fetching {endpoint} from {params[f'{param_name}>']} to {params[f'{param_name}<']}")
        month_data = await fetch_data_async(session, endpoint, params)
        if month_data:
            all_data.extend(month_data)
            logger.info(f"Total {endpoint} records so far: {len(all_data)}")

        current_date = next_date
        await asyncio.sleep(1)

    return all_data


def update_sync_progress(year_data, progress, message=None):
    """Update sync progress and message"""
    year_data.sync_progress = progress
    if message:
        year_data.sync_message = message
        current_app.logger.info(f"Sync progress {progress}%: {message}")
    db.session.commit()


def upsert_driver(driver_data):
    """Upsert a driver record"""
    driver = Driver.query.filter_by(
        driver_number=driver_data["driver_number"]
    ).first()
    if not driver:
        driver = Driver(driver_number=driver_data["driver_number"])
        db.session.add(driver)

    driver.full_name = driver_data.get("full_name", "")
    driver.team_name = driver_data.get("team_name", "")
    driver.team_colour = driver_data.get("team_colour", "")
    driver.country_code = driver_data.get("country_code", "")
    driver.headshot_url = driver_data.get("headshot_url", "")
    driver.last_updated = datetime.utcnow()
    return driver


def upsert_session(session_data, year):
    """Upsert a session record"""
    session = Session.query.filter_by(
        session_key=session_data["session_key"]
    ).first()
    if not session:
        session = Session(session_key=session_data["session_key"])
        db.session.add(session)

    session.session_name = session_data.get("session_name", "")
    session.date_start = (
        datetime.fromisoformat(session_data["date_start"].replace("Z", "+00:00"))
        if session_data.get("date_start")
        else None
    )
    session.date_end = (
        datetime.fromisoformat(session_data["date_end"].replace("Z", "+00:00"))
        if session_data.get("date_end")
        else None
    )
    session.gmt_offset = session_data.get("gmt_offset", "")
    session.session_type = session_data.get("session_type", "")
    session.meeting_key = session_data.get("meeting_key", 0)
    session.location = session_data.get("location", "")
    session.country_name = session_data.get("country_name", "")
    session.circuit_short_name = session_data.get("circuit_short_name", "")
    session.year = year
    return session


def upsert_driver_session(driver, session):
    """Upsert a driver session record"""
    driver_session = DriverSession.query.filter_by(
        driver_id=driver.id, session_id=session.id
    ).first()

    if not driver_session:
        driver_session = DriverSession(driver_id=driver.id, session_id=session.id)
        db.session.add(driver_session)

    return driver_session


@sync_bp.route("/data/<int:year>", methods=["POST"])
async def sync_f1_data(year):
    year_data = YearData.query.filter_by(year=year).first()
    if not year_data:
        year_data = YearData(year=year, sync_status="not_started", sync_progress=0)
        db.session.add(year_data)
        db.session.commit()

    try:
        logger = current_app.logger
        year_data.sync_status = "in_progress"
        year_data.sync_progress = 0
        db.session.commit()

        logger.info(f"Starting F1 data sync for {year}...")
        update_sync_progress(year_data, 5, "Initializing sync...")

        # Check if we already have session and driver data in the database
        existing_sessions = Session.query.filter_by(year=year).all()
        sessions_data = None
        all_drivers_data = None

        if existing_sessions:
            logger.info(
                f"Found {len(existing_sessions)} existing sessions in database for {year}"
            )
            sessions_data = [
                {
                    "session_key": s.session_key,
                    "session_name": s.session_name,
                    "session_type": s.session_type,
                    "date_start": s.date_start.isoformat() if s.date_start else None,
                    "location": s.location,
                }
                for s in existing_sessions
            ]

            # Get existing drivers from these sessions
            existing_drivers = (
                Driver.query.join(DriverSession)
                .join(Session)
                .filter(Session.year == year)
                .all()
            )
            logger.info(
                f"Found {len(existing_drivers)} existing drivers in database for {year}"
            )
            all_drivers_data = [
                {
                    "driver_number": d.driver_number,
                    "full_name": d.full_name,
                    "team_name": d.team_name,
                    "team_colour": d.team_colour,
                    "country_code": d.country_code,
                    "headshot_url": d.headshot_url,
                }
                for d in existing_drivers
            ]
        else:
            # STEP 1: Fetch sessions
            cached_sessions = SessionKeyCache.query.filter_by(year=year).all()
            if not cached_sessions:
                update_sync_progress(year_data, 10, "Fetching sessions...")
                async with aiohttp.ClientSession() as session:
                    sessions_data = await fetch_data_async(
                        session, "sessions", {"year": year}
                    )

                    if not sessions_data:
                        logger.error(f"No sessions found for {year}")
                        year_data.sync_status = "error"
                        year_data.sync_message = f"No sessions found for {year}"
                        db.session.commit()
                        return (
                            jsonify(
                                {
                                    "success": False,
                                    "error": f"No sessions found for year {year}",
                                }
                            ),
                            404,
                        )

                    logger.info(f"Caching {len(sessions_data)} sessions for {year}")
                    # Cache session keys
                    for sess in sessions_data:
                        cache_entry = SessionKeyCache(
                            year=year,
                            session_key=sess["session_key"],
                            session_name=sess.get("session_name"),
                            session_type=sess.get("session_type"),
                            date_start=(
                                datetime.fromisoformat(
                                    sess["date_start"].replace("Z", "+00:00")
                                )
                                if sess.get("date_start")
                                else None
                            ),
                            location=sess.get("location"),
                        )
                        existing = SessionKeyCache.query.filter_by(
                            year=year, session_key=sess["session_key"]
                        ).first()
                        if existing:
                            for key, value in vars(cache_entry).items():
                                if not key.startswith("_"):
                                    setattr(existing, key, value)
                        else:
                            db.session.add(cache_entry)
                    db.session.commit()
            else:
                logger.info(f"Using {len(cached_sessions)} cached sessions for {year}")
                sessions_data = [
                    {
                        "session_key": s.session_key,
                        "session_name": s.session_name,
                        "session_type": s.session_type,
                        "date_start": (
                            s.date_start.isoformat() if s.date_start else None
                        ),
                        "location": s.location,
                    }
                    for s in cached_sessions
                ]

            # Get session keys for driver filtering
            session_keys = [s["session_key"] for s in sessions_data]
            logger.info(f"Using session keys for filtering: {session_keys}")

            # Fetch drivers for each session
            all_drivers_data = []
            async with aiohttp.ClientSession() as session:
                for session_key in session_keys:
                    drivers = await fetch_data_async(
                        session, "drivers", {"session_key": session_key}
                    )
                    if drivers:
                        all_drivers_data.extend(drivers)

        # Process drivers if we have new data
        if not existing_sessions:
            update_sync_progress(year_data, 40, "Processing drivers...")
            unique_drivers = {}
            for driver in all_drivers_data or []:
                driver_num = driver.get("driver_number")
                if driver_num and driver_num not in unique_drivers:
                    unique_drivers[driver_num] = driver

            logger.info(f"Processing {len(unique_drivers)} unique drivers")
            # Upsert drivers
            for driver_data in unique_drivers.values():
                upsert_driver(driver_data)
            db.session.commit()

            update_sync_progress(year_data, 60, "Processing sessions...")

            # Process sessions and create driver sessions
            sessions = {}  # Keep track of session objects
            for session_data in sessions_data:
                session = upsert_session(session_data, year)
                sessions[session.session_key] = session
            db.session.commit()
            logger.info(f"Processed {len(sessions)} sessions")

        update_sync_progress(
            year_data, 20, "Checking and fetching position and lap data..."
        )

        # Check for existing position and lap data
        existing_positions = (
            Position.query.join(DriverSession)
            .join(Session)
            .filter(Session.year == year)
            .first()
        )
        existing_laps = (
            Lap.query.join(DriverSession)
            .join(Session)
            .filter(Session.year == year)
            .first()
        )

        positions_data = None
        laps_data = None
        positions_processed = 0
        laps_processed = 0

        async with aiohttp.ClientSession() as session:
            # For current year, use incremental updates if possible
            start_date = None
            if (
                year == datetime.now(timezone.utc).year
                and year_data.last_incremental_sync
                and existing_positions
                and existing_laps
            ):
                # Only use incremental sync date if we already have some data
                start_date = make_aware(year_data.last_incremental_sync).isoformat()
                logger.info(f"Using incremental sync from: {start_date}")
            else:
                # Use January 1st of the year with time component
                start_date = datetime(year, 1, 1, tzinfo=timezone.utc).isoformat()
                logger.info(f"Using full year sync from: {start_date}")

            # Set end date to now for current year, or end of year for past years
            end_date = (
                datetime.now(timezone.utc).isoformat()
                if year == datetime.now(timezone.utc).year
                else datetime(
                    year, 12, 31, 23, 59, 59, 999999, tzinfo=timezone.utc
                ).isoformat()
            )

            logger.info(f"Checking data status for {year}:")
            if not existing_positions:
                logger.info("No existing position data found, fetching...")
                positions_data = await fetch_data_by_month(
                    session, "position", start_date, end_date, "date"
                )
            else:
                logger.info("Found existing position data, skipping fetch")

            if not existing_laps:
                logger.info("No existing lap data found, fetching...")
                laps_data = await fetch_data_by_month(
                    session, "laps", start_date, end_date, "date_start"
                )
            else:
                logger.info("Found existing lap data, skipping fetch")

            # Only consider it a failure if we tried to fetch data and failed
            if (not existing_positions and not positions_data) or (
                not existing_laps and not laps_data
            ):
                logger.error(
                    "Failed to fetch required position or lap data. You can retry the sync to attempt fetching this data again."
                )
                year_data.sync_status = "incomplete"
                year_data.sync_message = "Some data fetch incomplete. Please retry."
                db.session.commit()
                return (
                    jsonify(
                        {
                            "success": False,
                            "error": "Failed to fetch required data. Please retry.",
                            "can_retry": True,
                            "missing_position_data": not existing_positions
                            and not positions_data,
                            "missing_lap_data": not existing_laps and not laps_data,
                        }
                    ),
                    500,
                )

            logger.info(f"Data status for {year}:")
            logger.info(
                f"- Positions: {'Using existing data' if existing_positions else f'Fetched {len(positions_data) if positions_data else 0} new records'}"
            )
            logger.info(
                f"- Laps: {'Using existing data' if existing_laps else f'Fetched {len(laps_data) if laps_data else 0} new records'}"
            )

        # Only process new data if we fetched it
        if positions_data:
            update_sync_progress(year_data, 70, "Processing new position data...")
            positions_processed = 0
            skipped_positions = 0

            # Process positions in batches to avoid memory issues
            batch_size = 1000
            for i in range(0, len(positions_data), batch_size):
                batch = positions_data[i : i + batch_size]

                for pos in batch:
                    try:
                        session_key = pos.get("session_key")
                        driver_number = pos.get("driver_number")

                        if not session_key or not driver_number:
                            logger.warning(
                                f"Skipping position record - missing key data: session_key={session_key}, driver_number={driver_number}"
                            )
                            skipped_positions += 1
                            continue

                        # Get or create driver session
                        driver_session = (
                            db.session.query(DriverSession)
                            .join(Session, DriverSession.session_id == Session.id)
                            .join(Driver, DriverSession.driver_id == Driver.id)
                            .filter(
                                Session.session_key == session_key,
                                Driver.driver_number == driver_number,
                            )
                            .first()
                        )

                        if not driver_session:
                            # Find the session and driver separately to debug which one might be missing
                            session = Session.query.filter_by(
                                session_key=session_key
                            ).first()
                            driver = Driver.query.filter_by(
                                driver_number=driver_number
                            ).first()

                            if not session:
                                logger.warning(
                                    f"Session not found for session_key: {session_key}"
                                )
                                skipped_positions += 1
                                continue

                            if not driver:
                                logger.warning(
                                    f"Driver not found for driver_number: {driver_number}"
                                )
                                skipped_positions += 1
                                continue

                            # Create new driver session
                            driver_session = DriverSession(
                                driver_id=driver.id, session_id=session.id
                            )
                            db.session.add(driver_session)
                            try:
                                db.session.flush()  # Ensure the driver_session gets an ID
                            except Exception as e:
                                logger.error(
                                    f"Failed to create driver session: {str(e)}"
                                )
                                db.session.rollback()
                                skipped_positions += 1
                                continue

                        # Add position with proper error handling
                        try:
                            position_date = make_aware(
                                datetime.fromisoformat(
                                    pos["date"].replace("Z", "+00:00")
                                )
                            )
                            position = Position(
                                driver_session_id=driver_session.id,
                                date=position_date,
                                position=pos["position"],
                            )
                            db.session.add(position)
                            positions_processed += 1

                            # Commit every 100 positions to avoid large transactions
                            if positions_processed % 100 == 0:
                                db.session.commit()
                                logger.info(
                                    f"Processed {positions_processed} positions..."
                                )

                        except Exception as e:
                            logger.error(f"Failed to create position record: {str(e)}")
                            db.session.rollback()
                            skipped_positions += 1
                            continue

                    except Exception as e:
                        logger.error(f"Error processing position record: {str(e)}")
                        db.session.rollback()
                        skipped_positions += 1
                        continue

                # Commit any remaining positions in this batch
                try:
                    db.session.commit()
                except Exception as e:
                    logger.error(f"Failed to commit batch: {str(e)}")
                    db.session.rollback()
                    continue

            logger.info(
                f"Position processing complete. Processed: {positions_processed}, Skipped: {skipped_positions}"
            )

            if skipped_positions > 0:
                logger.warning(
                    f"Skipped {skipped_positions} position records due to errors"
                )

        if laps_data:
            update_sync_progress(year_data, 80, "Processing new lap data...")
            # Process lap times
            # Clear existing laps for the affected period if we're updating
            if start_date and year == datetime.now(timezone.utc).year:
                deleted_count = Lap.query.filter(
                    Lap.driver_session_id.in_(
                        db.session.query(DriverSession.id)
                        .join(Session)
                        .filter(
                            Session.date_start
                            >= make_aware(datetime.fromisoformat(start_date))
                        )
                    )
                ).delete(synchronize_session="fetch")
                logger.info(
                    f"Deleted {deleted_count} existing laps for incremental update"
                )

            # Add new laps
            for lap in laps_data:
                if lap.get("lap_duration"):
                    session_key = lap.get("session_key")
                    driver_number = lap.get("driver_number")

                    if session_key and driver_number:
                        session = Session.query.filter_by(
                            session_key=session_key
                        ).first()
                        driver = Driver.query.filter_by(
                            driver_number=driver_number
                        ).first()

                        if session and driver:
                            driver_session = upsert_driver_session(driver, session)

                            new_lap = Lap(
                                driver_session_id=driver_session.id,
                                lap_number=lap.get("lap_number", 0),
                                lap_time=lap.get("lap_duration"),
                                lap_time_string=lap.get("lap_time_string"),
                            )
                            db.session.add(new_lap)
                            laps_processed += 1

            db.session.commit()
            logger.info(f"Processed {laps_processed} new laps")

        # Update year data
        year_data.drivers_count = (
            len(all_drivers_data)
            if all_drivers_data
            else Driver.query.join(DriverSession)
            .join(Session)
            .filter(Session.year == year)
            .count()
        )
        year_data.sessions_count = (
            len(sessions_data)
            if sessions_data
            else Session.query.filter_by(year=year).count()
        )
        year_data.last_synced = datetime.now(timezone.utc)
        if year == datetime.now(timezone.utc).year:
            year_data.last_incremental_sync = datetime.now(timezone.utc)
        year_data.sync_status = "completed"
        year_data.sync_progress = 100
        year_data.sync_message = "Sync completed successfully"
        db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Successfully synced F1 data for {year}",
                "drivers_processed": year_data.drivers_count,
                "sessions_processed": year_data.sessions_count,
                "positions_processed": positions_processed,
                "laps_processed": laps_processed,
                "year": year,
                "cached": False,
            }
        )

    except Exception as e:
        logger.error(f"General error: {str(e)}")
        if year_data:
            year_data.sync_status = "error"
            year_data.sync_message = str(e)
            db.session.commit()
        db.session.rollback()
        return jsonify({"success": False, "error": f"An error occurred: {str(e)}"}), 500


@sync_bp.route("/status/<int:year>", methods=["GET"])
def get_sync_status(year):
    """Get the current sync status for a year"""
    year_data = YearData.query.filter_by(year=year).first()
    if not year_data:
        return jsonify(
            {
                "status": "not_started",
                "progress": 0,
                "message": "No sync data available",
            }
        )

    return jsonify(
        {
            "status": year_data.sync_status,
            "progress": year_data.sync_progress,
            "message": year_data.sync_message,
            "last_synced": (
                year_data.last_synced.isoformat() if year_data.last_synced else None
            ),
            "last_incremental": (
                year_data.last_incremental_sync.isoformat()
                if year_data.last_incremental_sync
                else None
            ),
        }
    )


@sync_bp.route("/database/reset", methods=["POST"])
def reset_database():
    with sync_bp.app.app_context():
        try:
            # Drop all tables and recreate them
            db.drop_all()
            db.create_all()

            return jsonify({"success": True, "message": "Database reset successfully"})
        except Exception as e:
            return (
                jsonify(
                    {"success": False, "error": f"Failed to reset database: {str(e)}"}
                ),
                500,
            )


@sync_bp.route("/data/<int:year>/clear-laps", methods=["POST"])
def clear_lap_data(year):
    """Clear all lap data for a specific year"""
    try:
        # First get all sessions for the year
        sessions = Session.query.filter_by(year=year).all()
        session_ids = [s.id for s in sessions]

        # Get driver sessions for these sessions
        driver_sessions = DriverSession.query.filter(
            DriverSession.session_id.in_(session_ids)
        ).all()
        driver_session_ids = [ds.id for ds in driver_sessions]

        # Delete laps for these driver sessions
        deleted_count = Lap.query.filter(
            Lap.driver_session_id.in_(driver_session_ids)
        ).delete(synchronize_session="fetch")

        db.session.commit()

        # Also reset the year data to force a full sync
        year_data = YearData.query.filter_by(year=year).first()
        if year_data:
            year_data.last_incremental_sync = None
            db.session.commit()

        return jsonify(
            {
                "success": True,
                "message": f"Successfully deleted {deleted_count} lap records for {year}",
            }
        )
    except Exception as e:
        db.session.rollback()
        return (
            jsonify({"success": False, "error": f"Failed to clear lap data: {str(e)}"}),
            500,
        )
