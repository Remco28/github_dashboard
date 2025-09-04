# Phase 9 – Per‑Section Refresh & Cache Telemetry

## Objective
Improve responsiveness and user control by enabling refresh actions at the section level (without clearing the whole cache) and add lightweight cache hit/miss telemetry for observability.

## Scope
- Add optional cache‑bust support to cached wrappers used by specific sections so they can bypass TTL on demand.
- Add small “Refresh” actions to Visualizations, NEXT_STEPS, and Motivation sections only.
- Add in‑process cache telemetry (hits/misses, per‑function) and surface it in the sidebar cache panel.

## Files & Functions
- `services/cache.py`
  - Update `ttl_cache` decorator to record hit/miss counters.
  - Add module‑level metrics store `_cache_metrics` with totals and per‑function counts.
  - New function: `cache_metrics() -> dict` returning safe telemetry snapshot.
  - Extend cached wrappers to accept optional `cache_bust: str | None = None` so callers can force a new cache key:
    - `cached_list_repo_commits(owner, repo, token, since, until, cache_bust: str | None = None)`
    - `cached_fetch_next_steps(owner, repo, token, cache_bust: str | None = None)`
    - (Keep existing behavior when `cache_bust` is None.)
- `ui/notifications.py`
  - Update `render_cache_info(stats: dict)` to optionally display telemetry if present: total hits, misses, and hit rate; show top 3 function names by hits.
- `app.py`
  - Visualizations section: add a small `🔄 Refresh Charts` button. When pressed, compute `charts_cache_bust = str(time.time())` and pass as `cache_bust` to commit‑fetching paths.
  - NEXT_STEPS section: add `🔄 Refresh NEXT_STEPS` button, pass `cache_bust` to `cached_fetch_next_steps`.
  - Motivation section: add `🔄 Refresh Motivation` button, pass `cache_bust` through to the same commit‑fetch calls as charts.
  - Sidebar cache panel: if `cache_metrics()` is available, merge telemetry into the stats passed to `render_cache_info`.

## Detailed Requirements
- Cache telemetry
  - Totals: `hits`, `misses`, `hit_rate` (computed), `per_func` mapping `{ func_name: {hits, misses} }`.
  - Do not log arguments or values; function name only for privacy/safety.
  - Telemetry resets on process restart only; no persistence.
- Cache‑bust integration
  - Including `cache_bust` in the cached wrapper signature must alter the cache key such that a new value is computed while leaving the underlying service call signature unchanged.
  - Do NOT propagate `cache_bust` to GitHub API calls; it only affects cache keying.
- UX
  - Buttons appear inline with section headers or just beneath them; use concise labels listed above and unique Streamlit keys.
  - Global “Refresh” and “Bypass Cache” in the sidebar continue to work unchanged.
  - No per‑section clear‑all; only bypass for the next call via `cache_bust`.

## Constraints
- Keep API usage bounded: respect existing `max_repos` and pagination caps.
- No new external dependencies.
- Maintain light‑only theme (dark mode was removed previously).

## Acceptance Criteria
- Pressing `🔄 Refresh Charts` updates chart data even when global cache has fresh entries; other sections remain unaffected.
- Pressing `🔄 Refresh NEXT_STEPS` re‑fetches and re‑parses Markdown for selected repos without clearing other cache entries.
- Pressing `🔄 Refresh Motivation` recomputes streaks/badges based on freshly fetched commits.
- Sidebar cache panel shows: active entry count, cached function names, and (when available) total hits, misses, and hit rate.
- Normal operation (no buttons pressed) behaves exactly as before; no regressions in error handling or performance safeguards.

## Test Notes
- With a valid token, open the app and interact:
  - Trigger charts once, observe cache metrics increment (`misses` then `hits` on subsequent renders).
  - Press each section’s refresh button and verify fresh data without using “Clear Cache”.
  - Rate‑limit and auth error behavior remains unchanged (messages still come from `ui/notifications`).

