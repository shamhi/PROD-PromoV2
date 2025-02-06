from datetime import datetime, timedelta


def get_comment_date() -> str:
    now = datetime.utcnow()
    utc_plus_3 = now + timedelta(hours=3)

    return utc_plus_3


def format_rfc3339_date(date: datetime, tz: str) -> str:
    rfc3339 = datetime.strptime(date.isoformat(), "%Y-%m-%dT%H:%M:%S.%f")
    formatted_date = rfc3339.strftime("%Y-%m-%dT%H:%M:%S%z") + f"+{tz}"

    return formatted_date
