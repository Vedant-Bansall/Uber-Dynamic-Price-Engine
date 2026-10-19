import datetime

import config
import db.queries as q

start = datetime.datetime.fromisoformat(config.SEED_END_DATE) - datetime.timedelta(days=config.SEED_DAYS)
end = datetime.datetime.fromisoformat(config.SEED_END_DATE)

def test_ready():
    with q.get_connection(config.settings.test_db_name) as conn:
        rides = q.get_rides(conn=conn, start=start, end=end)
        pings = q.get_pings(conn=conn, start=start, end=end)
        zones = q.get_zones(conn=conn)

        rides_ready = (rides == 0) == rides.isna().sum().sum()
        pings_ready = (pings == 0) == pings.isna().sum().sum()
        zones_ready = (zones == 0) == zones.isna().sum().sum()
        assert len(rides) != 0
        assert len(pings) != 0
        assert len(zones) != 0
        assert rides_ready
        assert pings_ready
        assert zones_ready