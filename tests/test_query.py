import datetime
import uuid
from decimal import Decimal

from pandas.api import types
from pytest import approx

import db.queries as q

start = datetime.datetime.fromisoformat("2026-10-01T00:00:00+00:00") - datetime.timedelta(days=24)
end = start + datetime.timedelta(minutes=15)

def test_tables_start_empty(db_conn):
    with db_conn.cursor() as cur:
        zones_assertion = cur.execute("SELECT count(*) FROM zones").fetchone()
        rides_assertion = cur.execute("SELECT count(*) FROM rides").fetchone()
        driver_locations_assertion = cur.execute("SELECT count(*) FROM driver_locations").fetchone()
        pricing_logs_assertion = cur.execute("SELECT count(*) FROM pricing_logs").fetchone()

        assert zones_assertion[0] == 0
        assert rides_assertion[0] == 0
        assert driver_locations_assertion[0] == 0
        assert pricing_logs_assertion[0] == 0

# Rides Tests - I AM NOT COMMENTING AS THE NAMES ARE SELF EXPLANATORY
def test_get_rides_boundaries_singular(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO zones (zone_id, zone_name) VALUES (%s, %s)", (1, "Kristown"))
        cur.execute("INSERT INTO rides (ride_id, rider_id, pickup_zone_id, dropoff_zone_id, distance_miles, status, requested_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", (uuid.uuid4(), uuid.uuid4(), 1, 1, Decimal("4.67"), "completed", (start + datetime.timedelta(minutes=12, seconds=53))))
    db_conn.commit()

    rides = q.get_rides(db_conn, start, end)
    assert len(rides) == 1
    assert rides["distance_miles"].iloc[0] == 4.67

"""
_______________________________________________________
| Ride |          Time     	   | Distance | Returned? |
|  A   | start minus 1 second  |   1.00   |	   no     |
|  B   |     exactly start	   |   2.00   |	   yes    |
|  C   |  start plus 1 minute  |   3.00   |	   yes    |
|  D   |  end minus 1 second   |   4.00   |	   yes    |
|  E   |	  exactly end      |   5.00   |    no     |
|  F   |   end plus 1 second   |   6.00   |    no     |
‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾‾
"""

# Values
first = (uuid.uuid4(), uuid.uuid4(), 1, 1, 1.00, "completed", start - datetime.timedelta(seconds=1))
second = (uuid.uuid4(), uuid.uuid4(), 1, 1, 2.00, "completed", start)
third = (uuid.uuid4(), uuid.uuid4(), 1, 1, 3.00, "completed", start + datetime.timedelta(minutes=1))
fourth = (uuid.uuid4(), uuid.uuid4(), 1, 1, 4.00, "completed", end - datetime.timedelta(seconds=1))
fifth = (uuid.uuid4(), uuid.uuid4(), 1, 1, 5.00, "completed", end)
sixth = (uuid.uuid4(), uuid.uuid4(), 1, 1, 6.00, "completed", end + datetime.timedelta(seconds=1))

def test_get_rides_boundaries_multiple(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO zones (zone_id, zone_name) VALUES (%s, %s)", (1, "Kristown"))
        cur.executemany("INSERT INTO rides (ride_id, rider_id, pickup_zone_id, dropoff_zone_id, distance_miles, status, requested_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", ([fourth, second, sixth, third, first, fifth]))
    db_conn.commit()

    rides = q.get_rides(db_conn, start, end)
    assert len(rides) == 3
    assert (rides["distance_miles"].iloc[0] == approx(2.00)) and (rides["distance_miles"].iloc[1] == approx(3.00)) and (rides["distance_miles"].iloc[2] == approx(4.00))
    assert list(rides.columns.values) == ['ride_id', 'pickup_zone_id', 'dropoff_zone_id', 'distance_miles', 'status', 'requested_at']

def test_tz_aware_utc_rides(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO zones (zone_id, zone_name) VALUES (%s, %s)", (1, "Kristown"))
        cur.executemany("INSERT INTO rides (ride_id, rider_id, pickup_zone_id, dropoff_zone_id, distance_miles, status, requested_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", ([fourth, second, sixth, third, first, fifth]))
    db_conn.commit()

    rides = q.get_rides(db_conn, start, end)
    assert rides["requested_at"].dt.tz == datetime.timezone.utc  # noqa: UP017

def test_get_rides_empty_range_dtypes(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO zones (zone_id, zone_name) VALUES (%s, %s)", (1, "Kristown"))
        cur.executemany("INSERT INTO rides (ride_id, rider_id, pickup_zone_id, dropoff_zone_id, distance_miles, status, requested_at) VALUES (%s, %s, %s, %s, %s, %s, %s)", ([fourth, second, sixth, third, first, fifth]))
    db_conn.commit()

    rides = q.get_rides(db_conn, (start + datetime.timedelta(days=1)), (end + datetime.timedelta(days=1)))
    assert rides.empty
    assert types.is_object_dtype(rides["ride_id"])
    assert types.is_integer_dtype(rides["pickup_zone_id"])
    assert types.is_integer_dtype(rides["dropoff_zone_id"])
    assert types.is_float_dtype(rides["distance_miles"])
    assert types.is_string_dtype(rides["status"])
    assert types.is_datetime64_any_dtype(rides["requested_at"])

# Pings tests
def test_get_pings_boundaries_singular(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO zones (zone_id, zone_name) VALUES (%s, %s)", (1, "Kristown"))
        cur.execute("INSERT INTO driver_locations (ping_id, driver_id, driver, zone_id, is_available, ping_time) VALUES (%s, %s, %s, %s, %s, %s)", (458934705677823, uuid.uuid4(), "John Doe", 1, True, (start + datetime.timedelta(minutes=7, seconds=32))))
    db_conn.commit()

    pings = q.get_pings(db_conn, start, end)
    assert len(pings) == 1

# Values
pings_first = (458934705677823, uuid.uuid4(), "John Doe", 1, True, start - datetime.timedelta(seconds=1))
pings_second = (364125683423744, uuid.uuid4(), "John Doe", 1, True, start)
pings_third = (346278364782642, uuid.uuid4(), "John Doe", 1, False, start + datetime.timedelta(minutes=1))
pings_fourth = (437298723496924, uuid.uuid4(), "John Doe", 1, True, end - datetime.timedelta(seconds=1))
pings_fifth = (324987329487982, uuid.uuid4(), "John Doe", 1, False, end)
pings_sixth = (123872634989628, uuid.uuid4(), "John Doe", 1, True, end + datetime.timedelta(seconds=1))

def test_get_pings_boundaries_multiple(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO zones (zone_id, zone_name) VALUES (%s, %s)", (1, "Kristown"))
        cur.executemany("INSERT INTO driver_locations (ping_id, driver_id, driver, zone_id, is_available, ping_time) VALUES (%s, %s, %s, %s, %s, %s)", ([pings_fourth, pings_second, pings_sixth, pings_third, pings_first, pings_fifth]))
    db_conn.commit()

    pings = q.get_pings(db_conn, start, end)
    assert len(pings) == 3
    assert list(pings.columns.values) == ['ping_id', 'driver_id', 'zone_id', 'is_available', 'ping_time']
    assert (pings["ping_id"].iloc[0] == 364125683423744) and (pings["ping_id"].iloc[1] == 346278364782642) and (pings["ping_id"].iloc[2] == 437298723496924)
    assert (pings["is_available"].iloc[0] == True) and (pings["is_available"].iloc[1] == False) and (pings["is_available"].iloc[2] == True)

def test_tz_aware_utc_pings(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO zones (zone_id, zone_name) VALUES (%s, %s)", (1, "Kristown"))
        cur.executemany("INSERT INTO driver_locations (ping_id, driver_id, driver, zone_id, is_available, ping_time) VALUES (%s, %s, %s, %s, %s, %s)", ([pings_fourth, pings_second, pings_sixth, pings_third, pings_first, pings_fifth]))
    db_conn.commit()

    pings = q.get_pings(db_conn, start, end)
    assert pings["ping_time"].dt.tz == datetime.timezone.utc  # noqa: UP017

def test_get_pings_empty_range_dtypes(db_conn):
    with db_conn.cursor() as cur:
        cur.execute("INSERT INTO zones (zone_id, zone_name) VALUES (%s, %s)", (1, "Kristown"))
        cur.executemany("INSERT INTO driver_locations (ping_id, driver_id, driver, zone_id, is_available, ping_time) VALUES (%s, %s, %s, %s, %s, %s)", ([pings_fourth, pings_second, pings_sixth, pings_third, pings_first, pings_fifth]))
    db_conn.commit()

    pings = q.get_pings(db_conn, (start + datetime.timedelta(days=1)), (end + datetime.timedelta(days=1)))
    assert pings.empty
    assert types.is_integer_dtype(pings["ping_id"])
    assert types.is_object_dtype(pings["driver_id"])
    assert types.is_integer_dtype(pings["zone_id"])
    assert types.is_bool_dtype(pings["is_available"])
    assert types.is_datetime64_any_dtype(pings["ping_time"])