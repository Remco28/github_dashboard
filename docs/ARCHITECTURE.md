# Architecture Overview: GitHub Project Tracker Dashboard

This document sketches the current architecture shape so developers understand how components relate. It will evolve as features land.

## System Components

### Core Services
- Streamlit App (`app.py`) – UI shell, layout, filters, and user interactions; renders data provided by services.
- GitHub Client (`services/github_client.py`) – Thin REST client for GitHub API (pagination, timeouts, basic errors).
  - Error classification via `services/errors.py` (Phase 6): maps 401/403‑rate‑limit/404/other to typed exceptions for consistent UI handling.
- Cache (`services/cache.py`) – Simple in‑memory TTL cache to limit API calls and keep UI responsive.
- Analytics (`services/analytics.py`) – Chart‑ready aggregations (commits by day, repo stats, trends). Planned Phase 3.
 - NEXT_STEPS Parser (`services/next_steps.py`) – Fetches and parses `NEXT_STEPS.md` into actionable tasks. Implemented in Phase 4; rendered via `ui/checklists.py` with aggregate and repo detail views.
- Gamification (`services/gamification.py`) – Computes streaks, badges, and “stale repo” nudges. Implemented in Phase 5 with:
  - compute_activity_dates → set of active days from commit timestamps
  - compute_streaks → current/longest streaks across selected repos/time window
  - assign_badges → simple rules (e.g., weekly flame, marathon)
  - detect_stale_repos → days since push using RepoSummary.pushed_at
  - UI integration via `ui/gamification.py` (badges, streaks, nudges)
- Models (`models/github_types.py`) – Dataclasses for typed DTOs (e.g., `RepoSummary`).
- Settings (`config/settings.py`) – Env‑driven configuration (`GITHUB_TOKEN`, `GITHUB_USERNAME`).

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
  - gamification (streaks/badges/nudges)
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
- Gracefully handle missing/invalid files with guidance to add the template.

### Refresh & Rate Limits
```
user clicks Refresh → bypass cache → re‑fetch → update UI
```
- On 401/403, show friendly errors and suggest checking token/scope; never expose secrets.

## Key Abstractions

- RepoSummary – minimal repo view for tables/cards: name, visibility, stars, forks, open issues, last push, language, etc.
- TaskItem (planned) – parsed from `NEXT_STEPS.md` checkboxes with section context and status.
- Streak/Badge – derived metrics used by gamification.

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
- Performance: Keep API calls bounded; aggregate in memory using Pandas only where needed. Gamification reuses the same commit window and repo cap as charts.
- Resilience (Phase 6): Auth/Rate‑limit aware errors; unified notifications; cache controls (bypass/clear); consistent last‑updated indicators.
- Observability: minimal INFO logs (no secrets); show lightweight “last updated” indicators in UI.

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
- Current task spec: `comms/tasks/2025-09-03-foundations-and-data-fetch-mvp.md`
- Logging protocol: `comms/log.md`
