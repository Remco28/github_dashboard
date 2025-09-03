# Task Spec: UI Skeleton (Phase 2)

Author: Architect
Date: 2025-09-03
Status: SPEC READY

## Summary
Build the initial Streamlit UI skeleton with a sidebar for filters and a main area for summary metrics and a repositories table. Wire the UI to the existing data layer, keeping the services/UI boundaries clean. No advanced charts in this phase.

## Objectives
- Establish a consistent page layout and navigation anchors.
- Provide sidebar filters (language, visibility, activity window, search) and apply them client‑side.
- Render stat cards (totals) and a responsive, sortable repositories table.
- Keep the services layer UI‑agnostic; transformations live in a small analytics module.

## User Stories
- As a user, I can filter repositories by language, visibility (public/private), and recent activity window.
- As a user, I can quickly search repositories by name.
- As a user, I see high‑level stats update to reflect active filters.

## In Scope
- Sidebar controls and filter application.
- Stat cards and table with essential columns.
- Lightweight analytics helpers for transforms and filtering.

## Out of Scope (defer)
- Plotly charts (Phase 3).
- NEXT_STEPS.md integration (Phase 4).
- Gamification (Phase 5).

## Files and Functions
Create or update the following, with type hints and minimal, testable functions.

- `ui/components.py`
  - `def render_stat_cards(repo_summaries: list[RepoSummary]) -> None:`
    - Renders metrics: total repos, private count, archived count, (optional) languages count.
  - `def render_repo_table(repo_summaries: list[RepoSummary]) -> None:`
    - Displays a dataframe with columns: name, private, stars, forks, open issues, language, pushed_at (date), url.

- `services/analytics.py`
  - `def filter_repos(repos: list[RepoSummary], languages: set[str] | None, include_private: bool | None, activity_days: int | None, query: str | None) -> list[RepoSummary]:`
    - Applies filters. Activity filter compares `pushed_at` to now minus `activity_days`.
  - `def languages_set(repos: list[RepoSummary]) -> list[str]:` returns sorted unique languages (excluding None/empty).

- `app.py` (update)
  - Add sidebar controls:
    - Multiselect `Languages` from `languages_set()`.
    - Radio `Visibility`: All / Public / Private.
    - Slider `Activity Window (days)`: e.g., 7–365 with default 90.
    - Text input `Search` for repo name substring (case‑insensitive).
  - Apply filters via `services.analytics.filter_repos` before rendering.
  - Use `ui.components.render_stat_cards` and `ui.components.render_repo_table` for display.
  - Keep the existing Refresh button behavior.

## Constraints & Notes
- Do not introduce blocking network calls in UI functions; only operate on in‑memory data.
- Treat `pushed_at` as ISO string; parse with `datetime.fromisoformat` or `dateutil` (avoid new deps; handle trailing `Z` manually if needed).
- Handle empty states (no repos after filters) with clear messaging.

## Pseudocode

Sidebar and filtering:
```
langs = languages_set(repo_summaries)
sel_langs = st.sidebar.multiselect("Languages", options=langs)
visibility = st.sidebar.radio("Visibility", ["All", "Public", "Private"], index=0)
activity = st.sidebar.slider("Activity Window (days)", min_value=7, max_value=365, value=90)
query = st.sidebar.text_input("Search", "")

include_private = None if visibility == "All" else (visibility == "Private")
filtered = filter_repos(
    repo_summaries,
    set(sel_langs) if sel_langs else None,
    include_private,
    activity,
    query.strip() or None,
)
```

Filter function outline:
```
now = datetime.utcnow()
for r in repos:
  if languages and (not r.language or r.language not in languages): continue
  if include_private is not None and r.private != include_private: continue
  if activity_days is not None and r.pushed_at:
      # handle ISO format with Z
      dt = fromiso(r.pushed_at)
      if (now - dt).days > activity_days: continue
  if query and query.lower() not in r.name.lower(): continue
  yield r
```

## Acceptance Criteria
- Sidebar shows the four controls listed; changing any filter updates the table and stats.
- Stat cards reflect filtered set (counts match rows).
- Table renders the specified columns and supports sorting by at least stars and last push date.
- Empty state shows a friendly message and a quick way to clear filters.
- Performance: applying filters on 500 repos completes in under 200ms locally.

## Manual Test Plan
1) Launch app with `.env` configured.
2) Confirm default view shows totals and table with all repos.
3) Choose a language; verify only matching repos remain and stats update.
4) Toggle visibility to Private; verify only private repos remain.
5) Adjust activity window lower than the most recent push; verify older repos drop.
6) Type a partial name in Search; verify table filters accordingly.
7) Clear filters to return to full set.

## Deliverables
- Implemented `ui/components.py` and `services/analytics.py` with functions above.
- `app.py` updated to use sidebar and components.
- No new dependencies beyond what’s already in `requirements.txt`.

