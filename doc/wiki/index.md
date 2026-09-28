# NASA APOD viewer — codebase manual

Status as of the `feat/apod-mvp` merge to `main`: home page, past-date browsing, auth-aware navigation, seed data, and admin are shipped. Favorites are **not** implemented yet (see `doc/plan/` for the deferred plan).

## Stack

Django (6.1.x) with SQLite, Django's built-in `django.contrib.auth` and `django.contrib.admin`, server-rendered templates. No frontend framework. No HTTP client dependency — the NASA API is called with the standard library's `urllib.request` (see the study doc's reasoning: `requests` wasn't justified for one endpoint).

## Project layout

- `config/` — the Django project package (settings, root URLconf, WSGI/ASGI).
- `apod/` — the single app holding all current functionality: models, views, URLs, templates, admin, the seed management command, and tests.
- `doc/study/`, `doc/plan/` — the study and plan docs that produced this codebase.
- `manage.py`, `requirements.txt`, `.env.example`, `README.md` — standard project entry points.

## Data model

`apod.models.ApodEntry` (`apod/models.py`) is the only model. It's a local cache of NASA APOD API responses, keyed by `date` (unique):

- `date`, `title`, `explanation`
- `media_type` — `"image"` or `"video"`; the detail template branches on this to render an `<img>` or an `<iframe>`
- `url`, `hdurl` (nullable), `copyright` (blank-allowed)

There is no favorites/join model yet — that's the next planned addition.

## NASA API integration

`apod/services.py`:

- `get_or_fetch(entry_date)` is the single entry point views use. It looks up a cached `ApodEntry` for that date first; on a cache miss it calls the NASA API and saves the result. This means every date is fetched from NASA at most once, ever — subsequent views of the same date are pure DB reads.
- Raises `FutureDateError` for any date after today (checked before any API call), and `ApodFetchError` for network failures, non-2xx responses, or unparseable JSON. Views catch both and render a friendly in-page message instead of a 500.
- `_fetch_from_nasa` builds the request against `https://api.nasa.gov/planetary/apod` with `api_key` and `date` query params, using `NASA_API_KEY` from settings.

Caveat: the shared `DEMO_KEY` (used by default in a fresh `.env`) is rate-limited (~30-50 requests/day). A personal key from api.nasa.gov is recommended for anything beyond quick local checks.

## URLs and views

Routes are defined in `apod/urls.py` (namespaced `apod:`) and included at the project root in `config/urls.py`, alongside `django.contrib.auth.urls` under `accounts/` and the default `admin/`.

- `apod:home` (`/`) — today's picture. Calls `get_or_fetch(date.today())`.
- `apod:detail` (`/date/<entry_date>/`) — same rendering for an arbitrary date string (`YYYY-MM-DD`). Malformed date strings and future dates both render an error message rather than erroring or 404ing.
- `apod:archive_form` (`/archive/`) — a plain HTML date-picker form. Submitting it does a GET with `?date=...`, and the view redirects to `apod:detail` for that date.

All three of the above render `apod/templates/apod/apod_detail.html` for the actual picture, or `apod/templates/apod/archive_form.html` for the picker page.

## Templates and navigation

`apod/templates/base.html` is the shared layout every page extends. Its nav bar (Home / View a past date / Login-or-Logout) is present on every page — there is no page reachable only by typing a URL, per the project's navigation requirement. The logout control is a POST form (Django 5+ requires POST for logout), not a link.

`apod/templates/registration/login.html` overrides Django's default login template path so the login page matches the site's layout.

## Auth

Login/logout use Django's built-in auth views (`django.contrib.auth.urls`), not custom views. `LOGIN_REDIRECT_URL` and `LOGOUT_REDIRECT_URL` both point at `apod:home` (`config/settings.py`). There's no registration flow — accounts are created via the seed command or `createsuperuser`/admin, consistent with the project only needing Django's built-in auth.

## Admin

`ApodEntry` is registered in `apod/admin.py` with a list view (date, title, media type) and search over title/explanation. `User` management is Django's default admin, unmodified. There's no superuser created automatically — the README instructs running `createsuperuser` locally.

## Configuration

Settings (`config/settings.py`) read `SECRET_KEY`, `DEBUG`, `ALLOWED_HOSTS`, and `NASA_API_KEY` from environment variables via `os.environ`, with a small hand-rolled `_load_dotenv` helper that populates `os.environ` from a `.env` file if one exists (existing env vars always win). This avoids adding `python-dotenv`/`django-environ` as a dependency for a one-file, one-format need. `.env.example` documents the four required variables with no values; the real `.env` is gitignored.

Because `SECRET_KEY` and `NASA_API_KEY` are read with `os.environ[...]` (not `.get`), the app will fail fast at startup if `.env` is missing or incomplete, rather than silently running with defaults.

## Management commands

`apod/management/commands/seed_demo.py` (`python manage.py seed_demo`) is idempotent:

- Creates a `demo` user (password `apod-demo-pass`, documented in the README) if one doesn't exist.
- Seeds two historical `ApodEntry` rows (1995-06-16, the first-ever APOD, and 2015-06-16) so the archive view has something to show without needing a live NASA API call or a real API key.

Re-running it is safe — it skips anything that already exists.

## Testing

`apod/tests.py` covers the home page, past-date view (valid, future, and malformed dates), and nav auth state (login link vs. logout/username). All NASA API calls are mocked (`patch("apod.services._fetch_from_nasa")`) so tests never hit the network or burn real rate-limit quota, and they run against Django's throwaway test database — `db.sqlite3` is never touched by `manage.py test`.

## Known gaps / next steps

- Favorites (save a picture per user, list them on a favorites page) — deferred, not built. Will need a join model between `User` and `ApodEntry` and a login-required view.
- No registration flow for new users (by design — admin creates accounts, or use the seed command).
- No pagination or search on the admin's `ApodEntry` list beyond what Django admin gives for free.
