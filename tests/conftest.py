import pytest

from db.queries import get_connection


@pytest.fixture
def db_conn():
    with get_connection("pricing_test") as conn:
        with conn.cursor() as cur:
            cur.execute("TRUNCATE TABLE zones, rides, driver_locations, pricing_logs RESTART IDENTITY") # Remove existing data
        conn.commit()
        yield conn