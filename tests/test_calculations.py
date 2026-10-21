# Imports
import datetime

import pandas as pd

import pipeline.calculations as c

mock_df = pd.DataFrame({"ride_id": ["bdb1b01a-6202-417d-9368-8052543f0d90", "3035ac03-c6ea-4f86-bef5-4dc73b8de9fe", "ea8d1cdb-ca98-4007-8a9e-c791b4d2537c"], "pickup_zone_id": [5, 4, 1], "distance_miles": [5.95, 7.86, 2.08], "status": ["completed", "completed", "completed"], "requested_at": [datetime.datetime.fromisoformat("2026-09-03 00:00:07+00:00"), datetime.datetime.fromisoformat("2026-09-03 00:00:11+00:00"), datetime.datetime.fromisoformat("2026-09-03 00:00:20+00:00")]}) # Mock df used to test

def test_calculations(): # Function defining
    df = c.calculate_features(mock_df) # Getting calculated/edited DF

    assert not df.empty # Checks df isn't empty
    assert df["day_of_week"].isin([3]).all() # Checks that they all match the mock df value for day_of_week
    assert pd.api.types.is_integer_dtype(df["day_of_week"]) # Check it returns integer
    assert df["hour"].isin([0]).all() # Checks that they all match the mock df value for hour
    assert pd.api.types.is_integer_dtype(df["hour"]) # Checks it returns integer
    assert pd.api.types.is_bool_dtype(df["is_weekend"]) # Checks is_weekend is a boolean column
    assert pd.api.types.is_float_dtype(df["log_distance"]) # Checks log_distance is a float
    assert not pd.api.types.is_object_dtype(df["distance_miles"]) # Checks distance_miles isn't Decimal type (object - breaks scripts)
    assert list(df.columns.values) == ["ride_id", "pickup_zone_id", "distance_miles", "status", "requested_at", "day_of_week", "hour", "is_weekend", "log_distance"] # Checks the column names match up