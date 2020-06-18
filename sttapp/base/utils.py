import pytz


def get_local_dt(dt):
    tz = pytz.timezone('Asia/Taipei')
    utc = pytz.timezone('UTC')
    utc_dt = utc.localize(dt)
    tz_dt = utc_dt.astimezone(tz)
    return tz_dt
