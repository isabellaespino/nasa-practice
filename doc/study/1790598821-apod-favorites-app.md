# Study: NASA APOD viewer with user favorites

Date: 2026-09-28

## Request

A Django web app that:
- Shows today's Astronomy Picture of the Day (APOD) on the home page, with title, date, and explanation.
- Lets anyone view the picture for any past date.
- Lets registered/logged-in users save a picture to their favorites.
- Shows each user their own favorites list.
- Lets admins manage users via Django admin.

Stack constraint (per CLAUDE.md): Django, SQLite, Django's built-in auth and admin, server-rendered templates, no frontend framework, NASA APOD API.

## Feasibility

This is a small, well-bounded CRUD app on top of one external read-only API. Nothing in the request requires custom auth, a JS framework, or a non-relational store. Django's auth/admin cover login, logout, and user management out of the box. The only real design questions are (1) how to talk to the NASA APOD API, and (2) how to model "favorites" so they survive independently of that API. Both are straightforward. Overall: high confidence, low risk.

## NASA APOD API

- Endpoint: `https://api.nasa.gov/planetary/apod`, parameters include `api_key` and `date` (YYYY-MM-DD). Omitting `date` returns today's entry.
- Requires an API key from api.nasa.gov. The shared `DEMO_KEY` works but is rate-limited (roughly 30 requests/hour, 50/day), which is too low for a multi-user app even in testing. A free personal key raises this to ~1,000 requests/hour, which is fine for this project's scale.
- The key is a secret and must live in `.env`, referenced in code via `os.environ`, with `.env.example` documenting the `NASA_API_KEY` variable name (no value).
- Valid date range: the API's earliest entry is 1995-06-16. Requesting a date before that, or a future date, returns an error response. The "view past date" feature needs to validate input against `date.today()` as the upper bound; the lower bound can be soft (let the API reject it and surface the error) since NASA does not publish the boundary as a stable constant.
- Some days' entries are videos (`media_type: "video"`) rather than images, usually a YouTube embed URL. The home/detail template needs to branch on `media_type` rather than assuming an `<img>` tag always applies.
- Occasional entries have `copyright` fields that should probably be displayed for attribution, though it's not in the stated requirements — worth a one-line mention in the template but not required.

## Data model

Two things need to be modeled beyond Django's built-in `User`:

**A local record of APOD entries.** Favoriting requires something durable to point at — the NASA API has no concept of accounts or persistence, and re-fetching from NASA every time a favorite is rendered would be wasteful and fragile (an API outage would break a page that only shows *already-saved* data). The cleanest approach is a local table keyed by date, storing title, explanation, image/video URL, media type, and copyright, populated lazily the first time any user views or favorites that date. This turns the NASA API into a cache-filling source rather than a live dependency for every page render.

**A favorites join.** A many-to-many between `User` and the local APOD-entry table (through an explicit model if a "date favorited" timestamp is wanted, which seems useful for sorting the favorites page) records what each user has saved. Uniqueness should be enforced per (user, entry) pair so double-favoriting is a no-op rather than a duplicate row.

Tradeoff considered: fetch-and-display without ever caching, storing only `(user, date)` pairs for favorites and re-fetching from NASA on every favorites-page render. Rejected because it makes the favorites page dependent on NASA API uptime and rate limits indefinitely into the future, and re-fetches data that never changes once published. Caching costs a small amount of SQLite storage and one migration; that's a better trade.

## Pages and navigation

- Home (`/`): today's APOD. Fetches from NASA if not already cached locally for today's date, otherwise serves the cached copy.
- Archive/date view (`/apod/<date>/` or a date-picker form posting to it): same rendering as home, for an arbitrary past date. A simple `<input type="date">` form is enough; no JS needed since it's a plain GET/redirect.
- Login/logout: Django's built-in `django.contrib.auth` views, wired into `urls.py`, with a login link in the nav that swaps to a logout link (and username) once authenticated.
- Favorites (`/favorites/`): login-required view listing the current user's saved entries, likely newest-favorited first. Each home/archive page needs a "save to favorites" control, only shown/enabled to authenticated users, and only meaningful once that date's entry is cached locally (which it will be, since viewing the page is what caches it).
- Django admin (`/admin/`): enabled by default, gives admins user management immediately with zero extra code. Optionally register the APOD-entry and favorite models too for visibility, though not required by the request.

CLAUDE.md requires every page reachable via nav links, not just typed URLs — so the base template's nav needs: Home, an "View a past date" entry point (the date-picker page/form), Favorites (visible when logged in), Login/Logout, and a link to Admin is not required (admins can use the standard `/admin/` path directly, since that's Django convention and not really "app navigation").

## Dependency: HTTP client

Talking to the NASA API needs an HTTP client. Options:
- `urllib.request` (standard library, no new dependency): fine for a single simple GET with query params and JSON parsing. No compelling reason to avoid it here given how small the integration is.
- `requests`: nicer ergonomics (params dict, `.json()`, exceptions), but is an added dependency for something the stdlib already does adequately at this scale.

Recommendation: use `urllib.request` and avoid adding a dependency, since CLAUDE.md requires justifying any new dependency in a study and the ergonomic win from `requests` is marginal for one endpoint with one query pattern. If future work adds more external API calls, `requests` can be reconsidered then.

## Error handling and edge cases

- NASA API errors (bad key, rate limit, invalid date, network failure): the fetch layer should catch these and render a friendly "picture unavailable" state rather than a 500, especially since a NASA outage shouldn't break previously-cached pages.
- Future dates: reject client-side (validate against today's date) before ever calling the API.
- Favoriting requires login: unauthenticated users hitting the favorite action should be redirected to login (Django's `@login_required` handles this idiomatically) rather than erroring.
- Concurrent/duplicate favoriting: enforced at the DB level via a unique constraint on the join, so the view logic can just be "get or create" without race-prone check-then-insert logic.

## Testing approach

Per CLAUDE.md, use Django's test framework against a throwaway test DB, never the real `db.sqlite3`. The NASA API call should be mocked/stubbed in tests (both for speed and to not burn real rate-limit quota), verifying that: the home page renders cached vs. freshly-fetched entries correctly, invalid/future dates are rejected, favoriting requires auth, and the favorites page only shows the requesting user's own entries.

## Setup and seed data

CLAUDE.md requires the app not be empty on first clone. A management command or fixture that pre-populates a handful of well-known APOD dates (with their metadata) as local cache entries would let a fresh clone show a populated favorites-capable app even before anyone hits the live NASA API — useful in case a contributor doesn't have a NASA API key handy yet, though the home page will still need a real key to show *today's* picture live.

## Summary recommendation

Proceed. Model a local APOD-entry cache table plus a user-favorites join on top of Django's built-in `User`; use `urllib.request` rather than adding `requests`; validate dates client-side against today; mock the NASA API in tests. This fits entirely within the mandated stack with no new dependencies. Next step is a plan doc breaking this into ordered implementation steps.
