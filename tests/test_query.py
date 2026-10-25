import datetime
import uuid
from decimal import Decimal

import pandas as pd
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
    assert rides["pickup_zone_id"].dtype == int
    assert rides["dropoff_zone_id"].dtype == int
    assert rides["distance_miles"].dtype == float
    assert pd.api.types.is_string_dtype(rides["status"])
    assert pd.api.types.is_datetime64_any_dtype(rides["requested_at"])
    assert len(rides) == 3
    assert (rides["distance_miles"].iloc[0] == approx(2.00)) and (rides["distance_miles"].iloc[1] == approx(3.00)) and (rides["distance_miles"].iloc[2] == approx(4.00))
    assert (rides["requested_at"].iloc[0].tzinfo is not None) and (rides["requested_at"].iloc[0].tzinfo.utcoffset(rides["requested_at"].iloc[0]) is not None)
    print(list(rides.columns.values))
    assert list(rides.columns.values) == ['ride_id', 'pickup_zone_id', 'dropoff_zone_id', 'distance_miles', 'status', 'requested_at'] # Checks the column names match up
    assert q.get_rides(db_conn, (start + datetime.timedelta(days=1)), (end + datetime.timedelta(days=1))).empty