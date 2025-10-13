# Architecture Overview: GitHub Repository Dashboard

This document sketches the current architecture shape so developers understand how components relate. It will evolve as features land.

## System Components

### Core Services
- Streamlit App (`app.py`) – UI shell, layout, filters, and user interactions; renders data provided by services.
- GitHub Client (`services/github_client.py`) – Thin REST client for GitHub API (pagination, timeouts, basic errors).
  - Error classification via `services/errors.py` (Phase 6): maps 401/403‑rate‑limit/404/other to typed exceptions for consistent UI handling.
- Cache (`services/cache.py`) – Simple in‑memory TTL cache to limit API calls and keep UI responsive.
  - Phase 9: Adds cache telemetry (hits/misses per function, hit rate) via `cache_metrics()` and supports optional per‑call `cache_bust` in cached wrappers to bypass TTL for section‑level refreshes.
- Analytics (`services/analytics.py`) – Chart‑ready aggregations (commits by day, repo stats, trends). Implemented in Phase 3.
 - NEXT_STEPS Parser (`services/next_steps.py`) – Fetches and parses `NEXT_STEPS.md` into actionable tasks. Implemented in Phase 4; rendered via `ui/checklists.py` with aggregate and repo detail views.
- Models (`models/github_types.py`) – Dataclasses for typed DTOs (e.g., `RepoSummary`).
- Settings (`config/settings.py`) – Env‑driven configuration (`GITHUB_TOKEN`, `GITHUB_USERNAME`).

### UI Layer (Streamlit)
- `ui/styles.py` – One‑time global CSS and small JS injectors (header menu/deploy hider, Plotly card polish, compact DataFrame styles).
- `ui/headers.py` – Section header styles and `render_section_header()` helper (gradient highlight, :has() progressive enhancement).
- `ui/branding.py` – App branding helpers: `get_logo_base64()`, `render_app_title()`.
- `ui/controls.py` – Sidebar/help controls: repo selector with search, settings help panel.
- `ui/metrics.py` – Summary metric cards and `render_progress_circle()`.
- `ui/tables.py` – Repository details table rendering.
- `ui/charts.py` – Plotly chart renderers: language pie, commits bar, trend line, heatmap.
- `ui/checklists.py` – NEXT_STEPS aggregate view and per‑repo task lists.
- `ui/notifications.py` – Error/info utilities (cache info, section errors, last‑updated).

Notes:
- The former catch‑all `ui/components.py` has been decomposed to avoid a “god module”. Each module is cohesive and import cycles are avoided.
- `app.py` orchestrates these modules and owns high‑level layout; modules do not import from `app.py`.

### Supporting Services
- Database – None for MVP; consider SQLite later for optional persistence of custom goals or cached snapshots.
- Cache – In‑process dictionary; no external cache required.
- Message Broker – Not used.

### Process Architecture
```
[Streamlit UI (app.py)]
        |
        v
  [Services Layer]
  - github_client (REST)
  - cache (TTL)
  - analytics (charts)
  - next_steps (parsing)
  - cache metrics (telemetry)
  - errors (classification)
        |
        v
     [GitHub API]
```
Single process. UI calls service functions which may hit the GitHub API or return cached data.

## Data Flow Examples

### Load Dashboard (MVP)
```
start app → load settings → cached list_user_repos → map to RepoSummary → UI renders stat cards + table
```
- Caching reduces repeated API calls across re‑renders within a short TTL.

### Repo Detail + NEXT_STEPS (Integrated)
```
select repo → fetch `NEXT_STEPS.md` via GitHub Contents API → parse checklists/sections → UI displays tasks & aggregates (read‑only)
```
- Configurable processing limit (10-100 repos) with sidebar slider
- Smart prioritization by recent activity (pushed_at descending)
- Enhanced repository selector with search/filter for large lists
- Progress indicators and rate limit warnings for large processing sets
- Extended cache TTL (10 minutes) for NEXT_STEPS data
- Gracefully handle missing/invalid files with guidance to add the template.

### Refresh & Rate Limits
```
user clicks Refresh → bypass cache → re‑fetch → update UI
user clicks section Refresh (Charts/NEXT_STEPS) → bypass cache for that section only → update that section
```
- On 401/403, show friendly errors and suggest checking token/scope; never expose secrets.

## Key Abstractions

- RepoSummary – minimal repo view for tables/cards: name, visibility, stars, forks, open issues, last push, language, etc.
- TaskItem – parsed from `NEXT_STEPS.md` checkboxes with section context and status (implemented in Phase 4).

## Authentication & Authorization

- Personal Access Token (PAT) provided via environment; loaded at runtime.
- Trust boundaries: token remains server‑side within the local process; do not log or render the token.
- For deployment, use platform secrets; avoid embedding tokens in URLs.

## Configuration

- Module: `config/settings.py` loads env via `python-dotenv`.
- Required envs: `GITHUB_TOKEN`, `GITHUB_USERNAME`.
- Typical toggles (future): `LOG_LEVEL`, cache TTLs, default date ranges.

## Integration Points

- External APIs (GitHub):
  - `GET /user/repos?per_page=100&type=owner&sort=pushed` – list repos (paginated via `Link`).
  - `GET /repos/{owner}/{repo}/languages` – language byte map.
  - `GET /repos/{owner}/{repo}/contents/NEXT_STEPS.md` – fetch project tasks file (base64 contents).
- Error handling: raise concise `RuntimeError` on non‑2xx; surface user‑friendly Streamlit messages.
- Timeouts: ~10s per request; no aggressive retries for MVP.

## Runtime & Operations Notes

- Execution: `streamlit run app.py` launches the UI locally.
- Concurrency: Streamlit reruns scripts on interaction; use memoization/TTL cache for stability and speed.
- Performance: Keep API calls bounded; aggregate in memory using Pandas only where needed.
- Per-Section Refresh (Phase 9): Visualizations, NEXT_STEPS, and Motivation sections expose a small Refresh button. These trigger a one-off cache bypass using a timestamp `cache_bust` passed to cached wrappers; other sections remain unaffected.
- Resilience (Phase 6): Auth/Rate‑limit aware errors; unified notifications; cache controls (bypass/clear); consistent last‑updated indicators.
- Observability: minimal INFO logs (no secrets); show lightweight “last updated” indicators in UI.
  - Phase 9 Cache Telemetry: Sidebar cache panel displays active entries, cached function names, and cache performance (hits/misses, hit rate, top functions) sourced from `services/cache.cache_metrics()`.

### Time Handling
- External timestamps (GitHub API) arrive as ISO strings with `Z`. We parse to timezone‑aware UTC and normalize to safe comparisons.
- For API windows we build ISO strings with `Z` using `datetime.now(timezone.utc)`, stripping microseconds.
- For internal day/delta math we compare using naive UTC (timezone removed) to avoid naive/aware subtraction errors.

## Development Guidelines

### For Developers
- Keep services pure and UI‑agnostic; Streamlit code belongs in `app.py` and `ui/*`.
- Use the default Streamlit theme (light-only) for simplicity and consistency.
- Reuse small helpers (e.g., `parse_next_link`) and add type hints.
- Handle empty/edge cases (no repos, missing files) with clear UI states.

### For Architects/Tech Leads
- Update this document when adding new integration points (e.g., additional GitHub endpoints or persistence).
- Keep the focus on interactions and boundaries rather than implementation details.

## Related Docs

- Roadmap: `docs/ROADMAP.md`
- Specs: Current specs live in `comms/tasks/`; completed specs are archived in `comms/tasks/archive/`
- Logging protocol: `comms/log.md`
