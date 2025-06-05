from datetime import datetime
from extensions import db


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_number = db.Column(db.Integer, unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(50), nullable=True)
    team_colour = db.Column(db.String(7), nullable=True)
    country_code = db.Column(db.String(3), nullable=True)
    headshot_url = db.Column(db.String(255), nullable=True)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)
    is_active = db.Column(db.Boolean, default=False)

    sessions = db.relationship(
        "DriverSession", back_populates="driver", cascade="all, delete-orphan"
    )


class Session(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    session_key = db.Column(db.Integer, unique=True, nullable=False)
    session_name = db.Column(db.String(50), nullable=False)
    date_start = db.Column(db.DateTime, nullable=False)
    date_end = db.Column(db.DateTime, nullable=True)
    gmt_offset = db.Column(db.String(10), nullable=True)
    session_type = db.Column(db.String(20), nullable=False)
    meeting_key = db.Column(db.Integer, nullable=False)
    location = db.Column(db.String(100), nullable=True)
    country_name = db.Column(db.String(50), nullable=True)
    circuit_short_name = db.Column(db.String(50), nullable=True)
    year = db.Column(db.Integer, nullable=False)

    driver_sessions = db.relationship(
        "DriverSession", back_populates="session", cascade="all, delete-orphan"
    )


class DriverSession(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_id = db.Column(db.Integer, db.ForeignKey("driver.id"), nullable=False)
    session_id = db.Column(db.Integer, db.ForeignKey("session.id"), nullable=False)
    final_position = db.Column(db.Integer, nullable=True)
    fastest_lap = db.Column(db.Boolean, default=False)

    driver = db.relationship("Driver", back_populates="sessions")
    session = db.relationship("Session", back_populates="driver_sessions")
    positions = db.relationship(
        "Position", back_populates="driver_session", cascade="all, delete-orphan"
    )
    laps = db.relationship(
        "Lap", back_populates="driver_session", cascade="all, delete-orphan"
    )

    __table_args__ = (db.UniqueConstraint("driver_id", "session_id"),)


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_session_id = db.Column(
        db.Integer, db.ForeignKey("driver_session.id"), nullable=False
    )
    date = db.Column(db.DateTime, nullable=False)
    position = db.Column(db.Integer, nullable=False)

    driver_session = db.relationship("DriverSession", back_populates="positions")


class Lap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_session_id = db.Column(
        db.Integer, db.ForeignKey("driver_session.id"), nullable=False
    )
    lap_number = db.Column(db.Integer, nullable=False)
    lap_time = db.Column(db.Float, nullable=True)
    lap_time_string = db.Column(db.String(20), nullable=True)
    is_fastest = db.Column(db.Boolean, default=False)

    driver_session = db.relationship("DriverSession", back_populates="laps")

    __table_args__ = (db.UniqueConstraint("driver_session_id", "lap_number"),)


class YearData(db.Model):
    __tablename__ = "year_data"

    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, unique=True, nullable=False)
    sync_status = db.Column(
        db.String(20), default="not_started"
    )  # not_started, in_progress, completed, error, incomplete
    sync_progress = db.Column(db.Integer, default=0)
    sync_message = db.Column(db.String(200))
    last_synced = db.Column(db.DateTime)
    last_incremental_sync = db.Column(db.DateTime)
    drivers_count = db.Column(db.Integer)
    sessions_count = db.Column(db.Integer)


class SessionKeyCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    session_key = db.Column(db.String(100), nullable=False)
    session_name = db.Column(db.String(100))
    session_type = db.Column(db.String(50))
    date_start = db.Column(db.DateTime)
    location = db.Column(db.String(100))
    last_updated = db.Column(db.DateTime, default=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint("year", "session_key", name="unique_session_key_per_year"),
    )


class ConstructorStats(db.Model):
    __tablename__ = "constructor_stats"

    team_name = db.Column(db.String(50), nullable=False, primary_key=True)
    team_colour = db.Column(db.String(7), nullable=True)
    position = db.Column(db.Integer, nullable=False)
    points = db.Column(db.Integer, default=0)
    podiums = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    fastest_laps = db.Column(db.Integer, default=0)
    races = db.Column(db.Integer, default=0)
    year = db.Column(db.Integer, nullable=False, primary_key=True)

    __table_args__ = (db.UniqueConstraint("team_name", "year"),)


class DriverStats(db.Model):
    __tablename__ = "driver_stats"

    driver_number = db.Column(db.Integer, nullable=False, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(50), nullable=True)
    team_colour = db.Column(db.String(7), nullable=True)
    races = db.Column(db.Integer, default=0)
    country_code = db.Column(db.String(3), nullable=True)
    headshot_url = db.Column(db.String(255), nullable=True)
    position = db.Column(db.Integer, nullable=False)
    podiums = db.Column(db.Integer, default=0)
    wins = db.Column(db.Integer, default=0)
    fastest_laps = db.Column(db.Integer, default=0)
    points = db.Column(db.Integer, default=0)
    average_position = db.Column(db.Float, nullable=True)
    is_active = db.Column(db.Boolean, default=True)
    year = db.Column(db.Integer, nullable=False, primary_key=True)

    __table_args__ = (db.UniqueConstraint("driver_number", "year"),)


class DriverSessionStats(db.Model):
    __tablename__ = "driver_session_stats"

    driver_number = db.Column(db.Integer, nullable=False, primary_key=True)
    full_name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(50), nullable=True)
    session_name = db.Column(db.String(50), nullable=False, primary_key=True)
    session_type = db.Column(db.String(20), nullable=False, primary_key=True)
    location = db.Column(db.String(100), nullable=True)
    date_start = db.Column(db.DateTime, nullable=False, primary_key=True)
    final_position = db.Column(db.Integer, nullable=True)
    fastest_lap = db.Column(db.Boolean, default=False)
    points = db.Column(db.Integer, default=0)
    year = db.Column(db.Integer, nullable=False, primary_key=True)

    __table_args__ = (
        db.UniqueConstraint(
            "driver_number", "session_name", "session_type", "date_start", "year"
        ),
    )
