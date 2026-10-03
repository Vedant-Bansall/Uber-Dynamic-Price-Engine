import psycopg

with psycopg.connect("dbname=test user=postgres") as conn:
    with conn.cursor() as cur:
        cur.execute("""""")