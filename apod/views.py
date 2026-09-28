from datetime import date as date_cls, datetime

from django.shortcuts import redirect, render
from django.urls import reverse

from .services import ApodFetchError, FutureDateError, get_or_fetch


def _render_entry(request, entry_date):
    error = None
    entry = None
    try:
        entry = get_or_fetch(entry_date)
    except FutureDateError:
        error = "That date is in the future — the picture of the day for it doesn't exist yet."
    except ApodFetchError:
        error = "The picture for this date is unavailable right now. Please try again later."

    return render(
        request,
        "apod/apod_detail.html",
        {"entry": entry, "error": error, "entry_date": entry_date},
    )


def home(request):
    return _render_entry(request, date_cls.today())


def detail(request, entry_date):
    try:
        parsed_date = datetime.strptime(entry_date, "%Y-%m-%d").date()
    except ValueError:
        return _render_entry_invalid(request, entry_date)
    return _render_entry(request, parsed_date)


def _render_entry_invalid(request, raw_value):
    return render(
        request,
        "apod/apod_detail.html",
        {
            "entry": None,
            "error": f"'{raw_value}' isn't a valid date.",
            "entry_date": None,
        },
    )


def archive_form(request):
    requested = request.GET.get("date")
    if requested:
        return redirect(reverse("apod:detail", kwargs={"entry_date": requested}))
    return render(
        request,
        "apod/archive_form.html",
        {"max_date": date_cls.today().isoformat()},
    )
