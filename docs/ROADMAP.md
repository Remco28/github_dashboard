# GitHub Repository Dashboard – Roadmap

This roadmap breaks delivery into clear, reviewable stages. Each stage lists goals, scope, deliverables, acceptance criteria, and risks.

## Phase 0 – Foundations
- Status: Completed
- Goals: Repo scaffolding, env setup, GitHub PAT, dependencies, basic config.
- Scope: `requirements.txt`, `.env` loading, settings, minimal project structure.
- Deliverables: Bootable Streamlit app stub (`app.py`) that loads config; README quickstart.
- Acceptance: `streamlit run app.py` starts; token read from env; no runtime errors.

## Phase 1 – Data Fetch MVP
- Status: Completed
- Goals: Pull repositories and essential metadata via GitHub API.
- Scope: Repos list, last push, open issues, languages; basic caching.
- Deliverables: `services/github_client.py` with typed functions; `models` for DTOs.
- Acceptance: Local run fetches user repos successfully within rate limits; basic cache works.

## Phase 2 – UI Skeleton
- Status: Completed
- Goals: Streamlit layout and navigation.
- Scope: Sidebar filters (date range, language), main stat cards, repo table.
- Deliverables: `app.py` with layout; UI components for stat cards/table.
- Acceptance: Filters render; table paginates; no blocking calls on render (use caching).

## Phase 3 – Visualizations
- Status: Completed
- Goals: Core charts.
- Scope: Contribution heatmap (approx via commits by day), commits per repo bar, language pie, trend line.
- Deliverables: `ui/charts.py` (Plotly); chart-ready data functions in `services/analytics.py`; bounded commit fetch and caching.
- Acceptance: Charts render interactively; empty-state handling for sparse data.

## Phase 4 – Features Integration
- Status: Completed (migrated from NEXT_STEPS)
- Goals: Fetch and parse `comms/FEATURES.md` per repo; show feature delivery status.
- Scope: File detection, Markdown parse (sections, checkboxes), aggregate counts.
- Deliverables: `services/features.py` parser; UI checklist component; repo detail view; GitHub contents fetch and caching wrappers; aggregate totals in main view.
- Acceptance: For repos with the file, features display and aggregate totals compute; missing file shows guidance.

## Phase 5 – Gamification & Nudges
- Status: **Removed**
- **Note:** This feature was removed to better align the dashboard with its core purpose of providing a fast, focused overview of repository status. The "Nudges" concept for stale repos has been replaced by a sortable "Last Push" column in the main repository table.

## Phase 6 – Robustness & Performance
- Status: Completed
- Goals: Error handling, loading states, caching strategy.
- Scope: Graceful API failures, rate limit messaging, cache invalidation controls.
- Deliverables: Error classification (`services/errors.py`), bounded retry, unified notifications (`ui/notifications.py`), cache controls, last-updated indicators.
- Acceptance: App remains responsive under failures; rate limits show reset info; cache controls work.

## Phase 7 – Polish & Docs
- Status: Completed
- Goals: Usability polish, docs, and configuration.
- Scope: README usage, `.env.example`, configuration help.
- Deliverables: Updated README, `.env.example`, settings help panel.
- Acceptance: New user can set up and see charts quickly.

## Phase 8 – Optional Deployment
- Status: Completed
- Goals: Simple hosting option.
- Scope: Coolify (Nixpacks) deployment guide.
- Deliverables: Deploy guide; Procfile for Coolify.
- Acceptance: App deploys with secret config; renders charts remotely.

## Phase 9 – Per-Section Refresh & Cache Telemetry
- Status: Completed
- Goals: Improve responsiveness and observability.
- Scope: Section-level refresh buttons (Visualizations, Features), cache-bust support in cached wrappers, cache telemetry surfaced in sidebar.
- Deliverables: Updated `services/cache.py` with metrics and `cache_bust`; `app.py` buttons and wiring; cache panel enhancements.
- Acceptance: Section refresh bypasses TTL without clearing entire cache; sidebar shows hits/misses and hit rate.

## Phase 10 – Features Scalability
- Status: Completed
- Goals: Support processing 50-100+ repositories for Features with configurable limits.
- Scope: Sidebar slider for processing limit, smart prioritization by activity, enhanced repo selector with search, progress indicators, rate limit warnings.
- Deliverables: Updated `app.py` with configurable processing, search-enabled selector, extended cache TTL to 10 minutes.
- Acceptance: Configurable limit (10-100 repos), repositories sorted by recent activity, progress indicators for large sets.

## Phase 11 – Feature Refocus
- Status: Completed
- Goals: Simplify dashboard by removing low-value metrics and streamlining to FEATURES model.
- Scope: Remove Recent Activity section, remove PR columns (Open PRs, Needs Review, Stars, Forks), migrate NEXT_STEPS to FEATURES, default trend granularity to Weekly.
- Deliverables: Cleaner UI with focused repository table, FEATURES.md integration, updated tests and docs.
- Acceptance: No Recent Activity section, simplified table, Features sections working, all tests passing.

---

## Cross-Cutting Details
- Architecture: Python + Streamlit front end; `services/` for data, `ui/` for presentation, `models/` for types; caching at data layer.
- Config: `.env` with `GITHUB_TOKEN`, `GITHUB_USERNAME`; never committed.
- **Testing:** Automated `pytest` suite in `tests/` directory.
- **Metrics of Success:** Time-to-first-chart < 10 min; stale repos easily identifiable; Features aggregated; < 2s median interaction latency.

## Milestones & Checkpoints
1) MVP Usable (end Phase 3): repos table + core charts.
2) Actionable Insights (end Phase 4): Features checklists and aggregates.
3) **(Removed)** Motivation Layer
4) Shareable (end Phase 8): deployed or easy local run with docs.
5) UX Control & Observability (end Phase 9): per-section refresh and cache telemetry shipped.
6) Focused Dashboard (end Phase 11): streamlined UI with FEATURES model.

## Future Considerations

### Potential Enhancements
- Extended activity windows (730 days, "All time" with rate-limit guidance)
- "What's New Since Last Visit" feature
- Additional data sources beyond GitHub API
