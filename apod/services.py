import json
import urllib.error
import urllib.parse
import urllib.request
from datetime import date as date_cls

from django.conf import settings

from .models import ApodEntry

APOD_API_URL = "https://api.nasa.gov/planetary/apod"


class ApodFetchError(Exception):
    """Raised when the NASA APOD API can't be reached or returns an error."""


class FutureDateError(Exception):
    """Raised when a date after today is requested."""


def get_or_fetch(entry_date):
    """Return the ApodEntry for entry_date, fetching and caching it if needed."""
    if entry_date > date_cls.today():
        raise FutureDateError(f"{entry_date} is in the future")

    try:
        return ApodEntry.objects.get(date=entry_date)
    except ApodEntry.DoesNotExist:
        pass

    data = _fetch_from_nasa(entry_date)
    entry, _ = ApodEntry.objects.get_or_create(
        date=entry_date,
        defaults={
            "title": data.get("title", ""),
            "explanation": data.get("explanation", ""),
            "media_type": data.get("media_type", ApodEntry.IMAGE),
            "url": data.get("url", ""),
            "hdurl": data.get("hdurl") or None,
            "copyright": data.get("copyright", "") or "",
        },
    )
    return entry


def _fetch_from_nasa(entry_date):
    params = urllib.parse.urlencode(
        {"api_key": settings.NASA_API_KEY, "date": entry_date.isoformat()}
    )
    url = f"{APOD_API_URL}?{params}"
    try:
        with urllib.request.urlopen(url, timeout=10) as response:
            body = response.read()
    except urllib.error.HTTPError as exc:
        raise ApodFetchError(f"NASA API returned {exc.code}") from exc
    except urllib.error.URLError as exc:
        raise ApodFetchError(f"Could not reach NASA API: {exc.reason}") from exc

    try:
        return json.loads(body)
    except json.JSONDecodeError as exc:
        raise ApodFetchError("NASA API returned invalid JSON") from exc
