import datetime

import pandas as pd
import psycopg

import config


def get_connection(db_name=config.settings.db_name): # Function to get connection
    return psycopg.connect(dbname=db_name, host=config.settings.db_host, port=config.settings.db_port, user=config.settings.db_user, password=config.settings.db_password.get_secret_value()) # Creating and returning connection object

def get_rides(conn: psycopg.Connection, start: datetime.datetime, end: datetime.datetime) -> pd.DataFrame: # Params of connection object, period start time and period end time
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur: # Creating cursor object from connection
        rows = cur.execute("SELECT ride_id, pickup_zone_id, dropoff_zone_id, distance_miles, status, requested_at FROM rides WHERE requested_at >= %s AND requested_at < %s ORDER BY requested_at", (start, end)).fetchall() # Getting every row from rides with the start and end being params for the start and end times to filter by
        description = cur.description # Getting cursor description
        df = pd.DataFrame(rows, columns=[item.name for item in description]) # Creating DF
        df["requested_at"] = pd.to_datetime(df["requested_at"], utc=True) # Converting tz to UTC (There was an earlier bug that might happen might not so it is here just in case)
        df = df.astype({"pickup_zone_id": int, "dropoff_zone_id": int, "distance_miles": float, "status": str})
        return df # Return edited DF

def get_pings(conn: psycopg.Connection, start: datetime.datetime, end: datetime.datetime) -> pd.DataFrame: # Params of connection object, period start time and period end time
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur: # Creating cursor object from connection
        rows = cur.execute("SELECT ping_id, driver_id, zone_id, is_available, ping_time FROM driver_locations WHERE ping_time >= %s AND ping_time < %s ORDER BY ping_time", (start, end)).fetchall() # Getting every row from driver_locations with the start and end being params for the start and end times to filter by
        description = cur.description # Getting cursor description
        df = pd.DataFrame(rows, columns=[item.name for item in description]) # Creating DF
        df["ping_time"] = pd.to_datetime(df["ping_time"], utc=True) # Converting tz to UTC (There was an earlier bug that might happen might not so it is here just in case)
        df = df.astype({"ping_id": "Int64", "zone_id": int, "is_available": bool}) # Converting to certain dtypes for safety
        return df # Return edited DF

def get_zones(conn: psycopg.Connection) -> pd.DataFrame: # Param of connection object
    with conn.cursor(row_factory=psycopg.rows.dict_row) as cur: # Creating cursor object from connection
        rows = cur.execute("SELECT zone_id, zone_name FROM zones ORDER BY zone_id").fetchall() # Selecting everything from zones, no start or end time needed as there isn't any to filter this table by (it is just zone and zone id)
        description = cur.description # Getting cursor description
        return pd.DataFrame(rows, columns=[item.name for item in description]).astype({"zone_id": int, "zone_name": str}) # Returning DF straight away because there is no time filtering required/possible 