from extensions import db


class Driver(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_number = db.Column(db.Integer, unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    team_name = db.Column(db.String(50), nullable=True)
    team_colour = db.Column(db.String(7), nullable=True)
    country_code = db.Column(db.String(3), nullable=True)
    headshot_url = db.Column(db.String(255), nullable=True)
    is_active = db.Column(db.Boolean, default=False)

    sessions = db.relationship(
        "DriverSession", back_populates="driver", cascade="all, delete-orphan"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "driver_number": self.driver_number,
            "full_name": self.full_name,
            "team_name": self.team_name,
            "team_colour": self.team_colour,
            "country_code": self.country_code,
            "headshot_url": self.headshot_url,
            "is_active": self.is_active,
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "session_key": self.session_key,
            "session_name": self.session_name,
            "date_start": self.date_start.isoformat() if self.date_start else None,
            "date_end": self.date_end.isoformat() if self.date_end else None,
            "gmt_offset": self.gmt_offset,
            "session_type": self.session_type,
            "meeting_key": self.meeting_key,
            "location": self.location,
            "country_name": self.country_name,
            "circuit_short_name": self.circuit_short_name,
            "year": self.year,
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "driver_id": self.driver_id,
            "session_id": self.session_id,
            "final_position": self.final_position,
            "fastest_lap": self.fastest_lap,
        }


class Position(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    driver_session_id = db.Column(
        db.Integer, db.ForeignKey("driver_session.id"), nullable=False
    )
    date = db.Column(db.DateTime, nullable=False)
    position = db.Column(db.Integer, nullable=False)

    driver_session = db.relationship("DriverSession", back_populates="positions")

    def to_dict(self):
        return {
            "id": self.id,
            "driver_session_id": self.driver_session_id,
            "date": self.date.isoformat() if self.date else None,
            "position": self.position,
        }


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

    def to_dict(self):
        return {
            "id": self.id,
            "year": self.year,
            "sync_status": self.sync_status,
            "sync_progress": self.sync_progress,
            "sync_message": self.sync_message,
            "last_synced": self.last_synced.isoformat() if self.last_synced else None,
            "last_incremental_sync": (
                self.last_incremental_sync.isoformat()
                if self.last_incremental_sync
                else None
            ),
            "drivers_count": self.drivers_count,
            "sessions_count": self.sessions_count,
        }


class SessionKeyCache(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    year = db.Column(db.Integer, nullable=False)
    session_key = db.Column(db.String(100), nullable=False)
    session_name = db.Column(db.String(100))
    session_type = db.Column(db.String(50))
    date_start = db.Column(db.DateTime)
    location = db.Column(db.String(100))

    __table_args__ = (
        db.UniqueConstraint("year", "session_key", name="unique_session_key_per_year"),
    )

    def to_dict(self):
        return {
            "session_key": self.session_key,
            "session_name": self.session_name,
            "session_type": self.session_type,
            "date_start": self.date_start.isoformat() if self.date_start else None,
            "location": self.location,
        }


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

    def to_dict(self):
        return {
            "team_name": self.team_name,
            "team_colour": self.team_colour,
            "position": self.position,
            "points": self.points,
            "podiums": self.podiums,
            "wins": self.wins,
            "fastest_laps": self.fastest_laps,
            "races": self.races,
            "year": self.year,
        }


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

    def to_dict(self):
        return {
            "driver_number": self.driver_number,
            "full_name": self.full_name,
            "team_name": self.team_name,
            "team_colour": self.team_colour,
            "races": self.races,
            "country_code": self.country_code,
            "headshot_url": self.headshot_url,
            "position": self.position,
            "podiums": self.podiums,
            "wins": self.wins,
            "fastest_laps": self.fastest_laps,
            "points": self.points,
            "average_position": self.average_position,
            "is_active": self.is_active,
            "year": self.year,
        }


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

    def to_dict(self):
        return {
            "driver_number": self.driver_number,
            "full_name": self.full_name,
            "team_name": self.team_name,
            "session_name": self.session_name,
            "session_type": self.session_type,
            "location": self.location,
            "date_start": self.date_start.isoformat() if self.date_start else None,
            "final_position": self.final_position,
            "fastest_lap": self.fastest_lap,
            "points": self.points,
            "year": self.year,
        }
