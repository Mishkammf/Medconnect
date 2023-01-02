from datetime import datetime, timedelta

from exceptions.custom_exceptions import InvalidTimestampException


def get_valid_datetime(timestamp: str) -> datetime:
    try:
        if len(timestamp) == 10:
            return datetime.strptime(timestamp, "%Y-%m-%d")
        return datetime.strptime(timestamp, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        raise InvalidTimestampException(timestamp)


def validate_start_end_relativity(start_timestamp: datetime, end_timestamp: datetime) -> bool:
    if start_timestamp and end_timestamp and start_timestamp > end_timestamp:
        raise InvalidTimestampException(message=f"Start timestamp is greater than end timestamp")
    if end_timestamp - start_timestamp > timedelta(days=200):
        raise InvalidTimestampException(message=f"Select a date range spanning a maximum of 200 days")
    return True
