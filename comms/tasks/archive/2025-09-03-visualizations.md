# Task Spec: Visualizations (Phase 3)

Author: Architect
Date: 2025-09-03
Status: SPEC READY

## Summary
Implement core visualizations using Plotly and Streamlit, driven by existing data and a bounded commit aggregation. Provide: (1) approximate contribution heatmap, (2) commits per repository bar chart, (3) language distribution pie, and (4) commits over time line chart. Keep requests bounded to respect API limits and ensure the UI stays responsive.

## Objectives
- Add chart-ready data functions to `services/analytics.py`.
- Add optional, bounded commit fetch to `services/github_client.py` with basic caching.
- Render Plotly charts in a new `ui/charts.py` and integrate in `app.py` under a “Visualizations” section.

## User Stories
- As a user, I see an at-a-glance heatmap of recent activity.
- As a user, I can identify which repos I’ve committed to most in the selected window.
- As a user, I can see my languages mix and contribution trends over time.

## In Scope
- Charts listed above with simple, fast aggregations (bounded by a time window and repo count).
- Controls for time window reuse the existing Activity Window (days) slider.
- Basic empty-state handling for sparse data.

## Out of Scope (defer)
- Per-repo deep-dive pages.
- Client-side editing or annotations.

## Files and Functions

- `services/github_client.py` (update)
  - `def list_repo_commits(owner: str, repo: str, token: str, since: str, until: str, max_pages: int = 2) -> list[dict]:`
    - Calls `GET /repos/{owner}/{repo}/commits?since=<iso>&until=<iso>&per_page=100`.
    - Paginates via `Link` header up to `max_pages` to bound requests.
    - Returns raw commit JSON list (keep minimal processing here).

- `services/cache.py` (update)
  - Add cached wrapper: `cached_list_repo_commits(owner, repo, token, since, until)` with TTL ~300s.

- `services/analytics.py` (add)
  - `def language_distribution(repos: list[RepoSummary]) -> dict[str, int]:`
    - Counts repos by `language` (None excluded); returns mapping for pie chart.
  - `def commits_per_repo(repos: list[RepoSummary], token: str, since: str, until: str, max_repos: int = 10) -> list[tuple[str, int]]:`
    - For top `max_repos` by recent push (already in memory), fetch bounded commits and return `(repo_name, count)` sorted desc.
  - `def commits_over_time(repos: list[RepoSummary], token: str, since: str, until: str, max_repos: int = 10, freq: str = "W") -> list[tuple[str, int]]:`
    - Aggregate commit dates to bins (e.g., weekly) and return `(timestamp, total_commits)` sorted by time.
  - `def heatmap_counts(repos: list[RepoSummary], token: str, since: str, until: str, max_repos: int = 10) -> dict[str, int]:`
    - Return `{YYYY-MM-DD: count}` for daily commit totals to support a heatmap-like grid.
  - Notes: use cached commit fetch; guard for rate limits; if commits unavailable, fall back to counting `pushed_at` by day.

- `ui/charts.py` (new)
  - `def render_language_pie(lang_map: dict[str, int]) -> None`
  - `def render_commits_bar(data: list[tuple[str, int]]) -> None`
  - `def render_trend_line(points: list[tuple[str, int]]) -> None`
  - `def render_heatmap(day_counts: dict[str, int]) -> None`
  - Implement with Plotly; handle empty data with `st.info` and skip rendering.

- `app.py` (update)
  - Add a “Visualizations” section below the table; reuse `activity_days` for time window and derive `since/until` ISO.
  - Use a small `max_repos` selectbox (e.g., 5/10/20) in the sidebar for commit-based charts.
  - Wire to `ui.charts` rendering functions.

## API Endpoints
- `GET /repos/{owner}/{repo}/commits?since={iso}&until={iso}&per_page=100` — bounded commit listing.
- Headers: `Authorization: token <PAT>`, `Accept: application/vnd.github+json`.

## Constraints & Non‑functional Requirements
- Performance: Cap repos fetched for commits (default 10) and pages (default 2) to limit API calls and latency.
- Resilience: If commit calls fail (403/timeout), show a clear note and render charts that don’t require commits (e.g., language pie from in-memory repo data).
- UX: Charts should render quickly (<1–2s for default limits) and degrade gracefully to empty states.

## Pseudocode & Notes

Since/until window:
```
until = datetime.utcnow()
since = until - timedelta(days=activity_days)
iso = lambda dt: dt.replace(microsecond=0).isoformat() + 'Z'
```

Commits per repo (bounded):
```
selected = repos[:max_repos]  # already sorted by pushed_at desc
rows = []
for r in selected:
  owner, name = r.full_name.split('/', 1)
  commits = cached_list_repo_commits(owner, name, token, iso(since), iso(until))
  rows.append((r.name, len(commits)))
return sorted(rows, key=lambda x: x[1], reverse=True)
```

Heatmap counts:
```
counts = defaultdict(int)
for r in selected:
  for c in commits:
    dt = c['commit']['author'].get('date') or c['commit']['committer'].get('date')
    day = dt.split('T')[0]
    counts[day] += 1
return counts
```

## Acceptance Criteria
- Language Pie: Renders a pie with non-empty language categories from current filtered repos; empty state handled.
- Commits per Repo Bar: Shows top N repos by commit count over the selected window; N configurable in sidebar.
- Trend Line: Aggregates commits per week (or day) and renders a line; empty window shows an informative message.
- Heatmap: Renders a calendar-like daily intensity view for the window; if insufficient data, show fallback message.
- Performance: With defaults (N=10, 2 pages), charts render within ~2s on a typical account.
- Errors: API failures for commits do not crash the app; non-commit charts still render.

## Manual Test Plan
1) Launch app, confirm Visualizations section appears.
2) Adjust Activity Window; observe charts update sensibly.
3) Change max repos (5/10/20); confirm bar/trend/heatmap update and remain performant.
4) Temporarily use an invalid token to verify commit-based charts gracefully show an error while language pie remains.
5) Filter to a narrow set (e.g., one language) and verify charts reflect the subset.

## Deliverables
- New/updated modules and functions as listed.
- Integrated charts in `app.py` with sidebar control for max repos.
- No additional dependencies beyond Plotly (already present).

