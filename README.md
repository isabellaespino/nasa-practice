# NASA APOD viewer

A small Django app that shows NASA's Astronomy Picture of the Day (APOD) and lets you browse any past date. Favorites (saving pictures per logged-in user) are planned but not yet implemented — see `doc/plan/`.

## Stack

Django, SQLite, Django's built-in auth and admin, server-rendered templates. No frontend framework, no extra HTTP client dependency (uses the standard library's `urllib`).

## Setup

1. Clone the repo and `cd` into it.
2. Create and activate a virtualenv:
   ```
   python3 -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
4. Copy the environment template and fill it in:
   ```
   cp .env.example .env
   ```
   - `SECRET_KEY`: any random string for local development.
   - `DEBUG`: `True` for local development.
   - `ALLOWED_HOSTS`: e.g. `localhost,127.0.0.1,0.0.0.0`.
   - `NASA_API_KEY`: get a free key at https://api.nasa.gov (the shared `DEMO_KEY` also works but is heavily rate-limited).
5. Run migrations:
   ```
   python manage.py migrate
   ```
6. Seed a demo account and a couple of cached pictures:
   ```
   python manage.py seed_demo
   ```
   This creates a demo user (username `demo`, password `apod-demo-pass`) and seeds two historical APOD entries, so the app isn't empty even before you've viewed anything live.
7. Run the server:
   ```
   python manage.py runserver 0.0.0.0:8000
   ```
8. Visit `http://localhost:8000/`. Use the nav to view today's picture, browse a past date, or log in as the demo user.

## Admin

Create a superuser to manage users via Django admin:
```
python manage.py createsuperuser
```
Then visit `http://localhost:8000/admin/`.

## Tests

Tests run against Django's throwaway test database and mock the NASA API (no real network calls, no impact on `db.sqlite3`):
```
python manage.py test
```
