from datetime import datetime

__all__ = ['timestamp', 'formatted_datetime', 'first']


def timestamp():
    return datetime.utcnow()


def formatted_datetime(dt: datetime):
    assert dt is not None, "Datetime object is None."
    return dt.strftime("%Y-%m-%dT%H:%M:%SZ")


def first(item):
    if isinstance(item, list) and len(item) > 0:
        return item[0]
    else:
        return item
