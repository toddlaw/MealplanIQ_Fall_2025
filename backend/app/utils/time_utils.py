# time_utils.py
import datetime as dt
from zoneinfo import ZoneInfo

PT = ZoneInfo("America/Los_Angeles")

def pt_midnight_utc_ms(d: dt.date) -> int:
    pt_dt = dt.datetime(d.year, d.month, d.day, 0, 0, 0, tzinfo=PT)
    utc_dt = pt_dt.astimezone(dt.timezone.utc)
    return int(utc_dt.timestamp() * 1000)

def get_week_range():
    PT = ZoneInfo("America/Los_Angeles")
    now = dt.now(PT)
    start_date = now + dt.timedelta(days=1)        # 내일부터 시작
    end_date = start_date + dt.timedelta(days=6)   # 1주치
    today = now.date()

    return {
        "now": now,
        "today": today,
        "today_str": today.strftime("%Y-%m-%d"),
        "start_date": start_date,
        "end_date": end_date,
        "start_str": start_date.strftime("%Y-%m-%d"),
        "end_str": end_date.strftime("%Y-%m-%d"),
        "today_str": today.strftime("%Y-%m-%d")
    }
