# Task Spec: Robustness & Performance (Phase 6)

Author: Architect
Date: 2025-09-03
Status: SPEC READY

## Summary
Harden the app’s behavior under API failures, auth issues, and rate limits; unify error handling and user messaging; add cache controls and visibility. Keep UI responsive with consistent loading states and avoid crashes. Reuse existing data pathways and keep new logic thin and focused.

## Objectives
- Classify GitHub API responses into specific error types (auth, rate limit, not found, generic) and surface friendly UI messages.
- Add cache controls: bypass cache per-run, clear cache at runtime, and show basic cache statistics.
- Standardize loading and error messaging across sections (repos, charts, NEXT_STEPS, gamification, nudges).
- Provide a clear “last updated” indicator tied to data fetch operations.

## User Stories
- As a user, if my token is invalid, I see a clear message and how to fix it (without exposing secrets).
- As a user, if I hit rate limits, I see when limits reset and that data is temporarily stale.
- As a user, I can bypass cache or clear it when I need fresh data.
- As a user, the app stays responsive and doesn’t crash even if some API calls fail.

## In Scope
- Error classification for GitHub responses and targeted exceptions with metadata (e.g., rate-limit reset time).
- Centralized UI helpers to render consistent error/warning/info states.
- Cache utilities: in-memory cache clear and simple stats, plus a sidebar control.
- Minimal retries (optional) for transient network failures on idempotent GETs (bounded attempts, short backoff).

## Out of Scope (defer)
- Persistent caching to disk or DB.
- Full-featured observability/telemetry.
- Background jobs or prefetching.

## Files and Functions

- services/errors.py (new)
  - class GitHubApiError(Exception): fields: status:int, message:str
  - class AuthError(GitHubApiError)
  - class RateLimitError(GitHubApiError): fields: reset_epoch:int | None
  - class NotFoundError(GitHubApiError)
  - def classify_response(resp) -> None:
    - If 401 → raise AuthError.
    - If 403 and header `X-RateLimit-Remaining` == '0' → raise RateLimitError with `X-RateLimit-Reset`.
    - If 404 → raise NotFoundError.
    - If >=400 → raise GitHubApiError with truncated body.

- services/github_client.py (update)
  - Use `classify_response(response)` after each request; remove ad-hoc RuntimeError raises.
  - For endpoints where 404 maps to empty/None (e.g., contents, languages), handle NotFoundError to return default without surfacing to UI as error.
  - Add optional bounded retry for GETs on connection/timeouts (max 2 retries, 0.5s backoff).

- services/cache.py (update)
  - def clear_cache() -> None: empties in-memory store.
  - def cache_stats() -> dict: count, keys, earliest_expiry, latest_expiry (concise set; no PII/secret values).

- ui/notifications.py (new)
  - def render_error(e: Exception) -> None: maps AuthError → explicit token guidance; RateLimitError → reset time decoded; NotFoundError → info; GitHubApiError/other → generic warning.
  - def render_last_updated(ts: float | None) -> None: show localized timestamp or “Unknown”.

- app.py (update)
  - Sidebar: add “Bypass Cache” checkbox (in addition to Refresh), and “Clear Cache” button → calls `clear_cache()`.
  - Surface `render_last_updated(last_fetch_ts)` in header area for repos and for each bounded section.
  - Replace scattered `st.warning(... str(e))` with `render_error(e)` for API interactions in Visualizations, NEXT_STEPS, Motivation, and Nudges sections.
  - When RateLimitError is caught, skip dependent charts/sections for that render and show a compact message with reset time.

## Constraints & Non-Functional
- UX: No token or secret values ever displayed; messages must be actionable and concise.
- Performance: No additional API endpoints; retries bounded; error classification adds negligible overhead.
- Consistency: All sections use the same rendering helpers for errors and last-updated labels.

## Pseudocode
```
# services/errors.py
def classify_response(resp):
  if resp.status_code == 401: raise AuthError(401, "Unauthorized: check token scope")
  if resp.status_code == 403 and resp.headers.get('X-RateLimit-Remaining') == '0':
     reset = int(resp.headers.get('X-RateLimit-Reset', '0')) or None
     raise RateLimitError(403, "Rate limit exceeded", reset)
  if resp.status_code == 404: raise NotFoundError(404, "Not found")
  if resp.status_code >= 400: raise GitHubApiError(resp.status_code, truncate(resp.text))

# app.py (repos fetch example)
try:
  raw = cached_list_user_repos(..., cache_bust if bypass_cache else None)
  last_fetch_ts = time.time()
except Exception as e:
  render_error(e)

# ui/notifications.py
def render_error(e):
  if isinstance(e, AuthError): st.error("Authentication failed. Update your GitHub token in .env.")
  elif isinstance(e, RateLimitError):
     if e.reset_epoch: st.warning(f"Rate limit exceeded. Resets at {to_local(e.reset_epoch)}")
     else: st.warning("Rate limit exceeded. Try again later.")
  elif isinstance(e, NotFoundError): st.info("Requested item not found.")
  elif isinstance(e, GitHubApiError): st.warning(f"GitHub API error ({e.status}). Some data may be unavailable.")
  else: st.warning("Network error. Please retry or bypass cache.")
```

## Acceptance Criteria
- Authentication failures show a clear, actionable message; UI remains responsive.
- Rate limit conditions display a reset time (when provided) and hide dependent charts/sections for that render.
- “Bypass Cache” checkbox forces fresh fetches; “Clear Cache” empties TTL cache and shows a confirmation.
- “Last Updated” timestamps show after successful fetches for repos and major sections.
- All API error paths use `render_error` for consistent messaging; no raw tracebacks in UI.

## Manual Test Plan
1) Remove or invalidate token → verify AuthError message and other sections display placeholders, not crashes.
2) Simulate rate limit (or mock headers) → verify RateLimitError messaging includes human-readable reset time and that affected sections skip rendering.
3) Use “Bypass Cache” and “Clear Cache” → verify network calls occur again and cache size drops to zero; timestamps update.
4) Break a contents path to trigger NotFoundError → verify info message without failure of unrelated sections.
5) Introduce a network timeout (temporarily) → verify retry (if enabled) then friendly error with no crash.

