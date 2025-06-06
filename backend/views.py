from flask import current_app
from sqlalchemy import event, text
from extensions import db

VIEWS_SQL = {
    "driver_session_stats": """
    CREATE VIEW [driver_session_stats] AS
    SELECT
        d.driver_number,
        d.full_name,
        d.team_name,
        s.session_name,
        s.session_type,
        s.location,
        s.date_start,
        ds.final_position,
        ds.fastest_lap,
        s.year,
        CASE
            WHEN s.session_type = 'Race' AND s.session_name = 'Race' THEN
                CASE
                    WHEN ds.final_position = 1 THEN 25
                    WHEN ds.final_position = 2 THEN 18
                    WHEN ds.final_position = 3 THEN 15
                    WHEN ds.final_position = 4 THEN 12
                    WHEN ds.final_position = 5 THEN 10
                    WHEN ds.final_position = 6 THEN 8
                    WHEN ds.final_position = 7 THEN 6
                    WHEN ds.final_position = 8 THEN 4
                    WHEN ds.final_position = 9 THEN 2
                    WHEN ds.final_position = 10 THEN 1
                    ELSE 0
                END
            WHEN s.session_type = 'Race' AND s.session_name = 'Spring' THEN
                CASE
                    WHEN ds.final_position = 1 THEN 8
                    WHEN ds.final_position = 2 THEN 7
                    WHEN ds.final_position = 3 THEN 6
                    WHEN ds.final_position = 4 THEN 5
                    WHEN ds.final_position = 5 THEN 4
                    WHEN ds.final_position = 6 THEN 3
                    WHEN ds.final_position = 7 THEN 2
                    WHEN ds.final_position = 8 THEN 1
                    ELSE 0
                END
            ELSE 0
        END as points
    FROM driver_session ds
    JOIN driver d ON ds.driver_id = d.id
    JOIN session s ON ds.session_id = s.id
    """,
    "driver_stats": """
    CREATE VIEW [driver_stats] AS
    SELECT
        d.driver_number,
        d.full_name,
        d.team_name,
        d.team_colour,
        d.country_code,
        d.headshot_url,
        d.is_active,
        ds.year,
        COUNT(CASE WHEN ds.session_type = 'Race' AND ds.final_position IS NOT NULL THEN 1 END) as races,
        SUM(ds.points) as points,
        SUM(CASE WHEN ds.session_type = 'Race' AND ds.final_position = 1 THEN 1 ELSE 0 END) as wins,
        SUM(CASE WHEN ds.session_type = 'Race' AND ds.final_position >= 1 AND ds.final_position <= 3 THEN 1 ELSE 0 END) as podiums,
        SUM(CASE WHEN ds.session_type = 'Race' AND ds.fastest_lap = TRUE THEN 1 ELSE 0 END) as fastest_laps,
        AVG(CASE WHEN ds.session_type = 'Race' AND ds.final_position IS NOT NULL THEN ds.final_position END) as average_position,
        ROW_NUMBER() OVER (ORDER BY SUM(ds.points) desc) as position
    FROM driver_session_stats ds
    JOIN driver d ON ds.driver_number = d.driver_number
    GROUP BY d.driver_number, d.full_name, d.team_name, ds.year
    HAVING races > 0
    """,
    "constructor_stats": """
    CREATE VIEW [constructor_stats] AS
    SELECT
        d.team_name,
        d.team_colour,
        d.year,
        SUM(d.points) as points,
        SUM(d.wins) as wins,
        SUM(d.podiums) as podiums,
        SUM(d.fastest_laps) as fastest_laps,
        SUM(d.races) as races,
        ROW_NUMBER() OVER (ORDER BY SUM(d.points) desc) as position
    FROM driver_stats d
    WHERE d.team_name NOT NULL
    GROUP BY d.team_name, d.year
    """,
}

DROP_VIEWS_SQL = {
    "driver_session_stats": """
    DROP VIEW IF EXISTS [driver_session_stats];
    """,
    "driver_stats": """
    DROP VIEW IF EXISTS [driver_stats];
    """,
    "constructor_stats": """
    DROP VIEW IF EXISTS [constructor_stats];
    """,
}


@event.listens_for(db.metadata, "after_create")
def create_views(target, connection, **kw):
    """Creates views if they don't exist."""
    if not current_app.config.get("TESTING"):
        for sql in DROP_VIEWS_SQL.values():
            connection.execute(text(sql))
        for sql in VIEWS_SQL.values():
            connection.execute(text(sql))


def register_view_creation(app):
    with app.app_context():
        event.listen(db.metadata, "after_create", create_views) 