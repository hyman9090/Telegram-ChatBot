from datetime import datetime
from datetime import timedelta
import pytz
import math


def convert_timestamp(timestamp: datetime) -> datetime:
    to_timezone = pytz.timezone("Asia/Hong_Kong")  # UTC+8
    return timestamp.astimezone(to_timezone)


def second2HHMMSS(seconds: timedelta) -> str:
    s = int(seconds.total_seconds())

    day_seconds = 86_400
    hour_seconds = 3_600
    min_seconds = 60

    days = math.floor(s / day_seconds)
    hours = math.floor((s - days) / hour_seconds)
    mins = math.floor((s - days * day_seconds - hours * hour_seconds) / 60)
    secs = s - days * day_seconds - hours * hour_seconds - mins * min_seconds

    if days > 0:
        return f"{days}Days {hours}Hours {mins}Minutes {secs}Seconds"
    elif hours > 0:
        return f"{hours}Hours {mins}Minutes {secs}Seconds"
    elif mins > 0:
        return f"{mins}Minutes {secs}Seconds"
    else:
        return f"{secs}Seconds"
