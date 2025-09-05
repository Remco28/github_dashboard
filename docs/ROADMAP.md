# GitHub Project Tracker Dashboard – Roadmap

This roadmap breaks delivery into clear, reviewable stages aligned to PROJECT.md. Each stage lists goals, scope, deliverables, acceptance criteria, and risks. Time estimates assume part‑time execution.

## Phase 0 – Foundations (0.5–1 day)
- Status: Completed
- Goals: Repo scaffolding, env setup, GitHub PAT, dependencies, basic config.
- Scope: `requirements.txt`, `.env` loading, settings, minimal project structure.
- Deliverables: Bootable Streamlit app stub (`app.py`) that loads config; README quickstart.
- Acceptance: `streamlit run app.py` starts; token read from env; no runtime errors.
- Risks: Token mishandling. Mitigation: `.env` + `.gitignore`, dotenv.

## Phase 1 – Data Fetch MVP (0.5–1 day)
- Status: Completed
- Goals: Pull repositories and essential metadata via GitHub API.
- Scope: Repos list, last push, stars, forks, open issues, languages; basic caching.
- Deliverables: `services/github_client.py` with typed functions; `models` for DTOs.
- Acceptance: Local run fetches user repos successfully within rate limits; basic cache works.
- Risks: Rate limits. Mitigation: simple TTL cache, fetch-on-demand.

## Phase 2 – UI Skeleton (0.5 day)
- Status: Completed
- Goals: Streamlit layout and navigation.
- Scope: Sidebar filters (date range, language), main stat cards, repo table.
- Deliverables: `app.py` with layout; `ui/components.py` for stat cards/table.
- Acceptance: Filters render; table paginates; no blocking calls on render (use caching).
- Risks: Slow renders. Mitigation: cache and memoize data transforms.

## Phase 3 – Visualizations (1 day)
- Status: Completed
- Goals: Core charts per PROJECT.md.
- Scope: Contribution heatmap (approx via commits by day), commits per repo bar, language pie, trend line.
- Deliverables: `ui/charts.py` (Plotly); chart-ready data functions in `services/analytics.py`; bounded commit fetch and caching in `services/github_client.py`/`services/cache.py`; `app.py` section "Visualizations" with sidebar control for max repos.
- Acceptance: Charts render interactively; empty‑state handling for sparse data.
- Risks: Commit aggregation volume. Mitigation: bounded time window + caching.

## Phase 4 – NEXT_STEPS Integration (1 day)
- Status: Completed
- Goals: Fetch and parse `NEXT_STEPS.md` per repo; show actionable tasks.
- Scope: File detection, Markdown parse (sections, checkboxes), aggregate counts.
- Deliverables: `services/next_steps.py` parser; UI checklist component; repo detail view; GitHub contents fetch and caching wrappers; aggregate totals in main view.
- Acceptance: For repos with the file, tasks display and aggregate totals compute; missing file shows guidance.
- Risks: Format drift. Mitigation: tolerant parser + template link.

## Phase 5 – Gamification & Nudges (0.5–1 day)
- Status: Completed
- Goals: Motivational badges, streaks, gentle reminders.
- Scope: Current/longest commit streak, stale repo list, badge logic.
- Deliverables: `services/gamification.py`; badges in header; nudges block.
- Acceptance: Badges derive from data consistently; stale repos sorted by inactivity.
- Risks: Perceived judgment. Mitigation: playful copy, opt‑out toggle.

## Phase 6 – Robustness & Performance (0.5 day)
- Status: Completed
- Goals: Error handling, loading states, caching strategy.
- Scope: Graceful API failures, rate limit messaging, cache invalidation controls.
- Deliverables: Error classification (`services/errors.py`), bounded retry, unified notifications (`ui/notifications.py`), cache controls (`clear_cache`, `cache_stats`, bypass), last‑updated indicators, and section‑level graceful degradation.
- Acceptance: App remains responsive under failures; rate limits show reset info; cache controls work; standardized messages across sections.

## Phase 7 – Polish & Docs (0.5 day)
- Status: Completed
- Goals: Usability polish, docs, and configuration.
- Scope: Theming toggle (later removed via Phase 2025-09-04 Remove Dark Mode), README usage, `.env.example`, configuration help.
- Deliverables: Updated README, screenshots/gifs, `.env.example`, settings help panel.
- Acceptance: New user can set up and see charts within 10 minutes.

## Phase 8 – Optional Deployment (0.5 day)
- Status: Completed
- Goals: Simple hosting option.
- Scope: Streamlit Community Cloud instructions; alt: Dockerfile.
- Deliverables: Deploy guide; minimal Dockerfile (optional).
- Acceptance: App deploys with secret config; renders charts remotely.

---

## Cross‑Cutting Details
- Architecture: Python + Streamlit front end; `services/` for data, `ui/` for presentation, `models/` for types; caching at data layer.
- Config: `.env` with `GITHUB_TOKEN`, `GITHUB_USERNAME`; never committed.
- Testing: Manual runs; spot unit tests for parsers and analytics as time allows.
- Metrics of Success: Time‑to‑first‑chart < 10 min; stale repo surfaced; NEXT_STEPS aggregated; streaks visible; < 2s median interaction latency.

## Milestones & Checkpoints
1) MVP Usable (end Phase 3): repos table + core charts.
2) Actionable Insights (end Phase 4): NEXT_STEPS checklists and aggregates.
3) Motivation Layer (end Phase 5): badges, streaks, stale nudges.
4) Shareable (end Phase 8): deployed or easy local run with docs.
5) UX Control & Observability (end Phase 9): per‑section refresh and cache telemetry shipped.

## Phase 9 – Per‑Section Refresh & Cache Telemetry (0.5 day)
- Status: Completed
- Goals: Improve responsiveness and observability.
- Scope: Section‑level refresh buttons (Visualizations, NEXT_STEPS, Motivation), cache‑bust support in cached wrappers, cache telemetry surfaced in sidebar.
- Deliverables: Updated `services/cache.py` with metrics and `cache_bust`; `app.py` buttons and wiring; `ui/notifications.py` cache panel enhancements; analytics passthrough of `cache_bust`.
- Acceptance: Section refresh bypasses TTL without clearing entire cache; sidebar shows hits/misses and hit rate; no regressions in rate‑limit handling.

## Phase 10 – NEXT_STEPS Scalability (Completed)
- Status: Completed
- Goals: Support processing 50-100+ repositories for NEXT_STEPS with configurable limits
- Scope: Sidebar slider for processing limit, smart prioritization by activity, enhanced repo selector with search, progress indicators, rate limit warnings
- Deliverables: Updated `app.py` with configurable processing, `ui/components.py` with search-enabled selector, extended cache TTL to 10 minutes
- Acceptance: Configurable limit (10-100 repos), repositories sorted by recent activity, progress indicators for large sets, search/filter in dropdown, rate limit warnings
- Risks: Rate limit exhaustion mitigated with warnings and caps

## Next Actions (Spec Handoff)
- Author Phase 0–1 spec in `comms/tasks/` with file/function names and acceptance tests.
- After implementation, review against acceptance criteria; iterate or proceed to next phase.
