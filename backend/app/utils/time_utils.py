# time_utils.py
import datetime as dt
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")

def pt_midnight_utc_ms(d: dt.date) -> int:
    pt_dt = dt.datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=PT)
    utc_dt = pt_dt.astimezone(dt.timezone.utc)
    return int(utc_dt.timestamp() * 1000)
