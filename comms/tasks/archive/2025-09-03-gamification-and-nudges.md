# Task Spec: Gamification & Nudges (Phase 5)

Author: Architect
Date: 2025-09-03
Status: SPEC READY

## Summary
Introduce a motivation layer with streaks, badges, and gentle “stale repo” nudges. Use existing commit data and repo metadata to compute current/longest activity streaks, assign simple badges, and surface repositories that need attention. Render a compact badge strip and a nudges panel in the UI without adding heavy API load.

## Objectives
- Compute current and longest activity streaks based on commit activity within a bounded time window.
- Assign a small set of badges (e.g., streak milestones, productivity) derived from streaks and totals.
- Detect and list “stale” repositories (no pushes beyond threshold), sorted by inactivity.
- Display badges and streaks prominently; show a nudge list with quick context.

## User Stories
- As a user, I see my current and longest streak so I stay motivated.
- As a user, I earn badges (e.g., 7-day streak, 30 commits this month) that make progress feel rewarding.
- As a user, I see which repositories are getting stale so I can prioritize them.

## In Scope
- Streaks computed from days with any commits across the selected/bounded set of repositories.
- Basic badges derived from streaks and commit counts (read-only display).
- Stale repos based on `pushed_at` in `RepoSummary` with a user-controlled threshold (e.g., slider).
- UI components for badges, streaks, and nudges; integrated into `app.py`.

## Out of Scope (defer)
- Per-user commit author verification (email mapping) — treat any commit on owned repos as activity.
- Writing reminders/issues to GitHub; notifications.
- Animated badge graphics beyond emojis and Streamlit components.

## Files and Functions

- services/gamification.py (new)
  - from dataclasses import dataclass
  - @dataclass class StreakStats: fields: current:int, longest:int, last_active:str | None
  - @dataclass class Badge: fields: key:str, label:str, emoji:str, description:str
  - def compute_activity_dates(commits_by_repo: dict[str, list[dict]]) -> set[str]:
    - Extract unique UTC dates (YYYY-MM-DD) from commit timestamps across repos.
  - def compute_streaks(activity_dates: set[str], until: str) -> StreakStats:
    - Walk backwards from `until` date day-by-day while date in set to get current; compute longest by scanning contiguous runs.
  - def assign_badges(streaks: StreakStats, total_commits: int) -> list[Badge]:
    - Rules: current>=7 ("Weekly Flame"), longest>=30 ("Marathon"), total>=50 ("Prolific"), current==0 ("Welcome Back" nudge badge).
  - def detect_stale_repos(repos: list[RepoSummary], threshold_days:int) -> list[tuple[RepoSummary,int]]:
    - Return list of tuples (repo, days_since_push) for repos exceeding threshold, sorted desc by days_since_push.

- services/cache.py (update)
  - Add @ttl_cache(300) wrappers:
    - cached_compute_streaks(activity_dates: tuple[str, ...], until: str) -> StreakStats
    - cached_detect_stale_repos(keys that are hashable) or rely on lightweight computation (optional; acceptable to skip if complexity low).

- ui/gamification.py (new)
  - def render_badges(badges: list[Badge]) -> None: horizontal chips with emoji and tooltips.
  - def render_streaks(stats: StreakStats) -> None: show current/longest with a small progress-style visual.
  - def render_stale_nudges(items: list[tuple[RepoSummary,int]], limit:int=5) -> None: list top-N with days stale and repo link.

- app.py (update)
  - Add a new section “Motivation” (badges + streaks) and a “Nudges” panel below it.
  - Reuse the same `since`/`until` window and `max_repos` bound as charts to limit API calls.
  - For the repos subset, fetch commits using existing `cached_list_repo_commits`, aggregate by date, compute streaks and badges.
  - Provide a sidebar control: “Stale Threshold (days)” default 30.

## Constraints & Non-Functional
- Performance: Bound work to selected `max_repos`; rely on existing caching for commits; avoid new endpoints.
- Resilience: Empty or sparse data should produce zeroed stats and friendly messages.
- Security: No secrets in logs; no PII assumptions about commit authors.

## Pseudocode
```
# In app.py, after computing since/until and selecting repos[:max_repos]
commits_by_repo = {}
for r in selected_repos:
  owner, name = r.full_name.split('/', 1)
  commits = cached_list_repo_commits(owner, name, token, since_iso, until_iso)
  commits_by_repo[r.full_name] = commits

dates = compute_activity_dates(commits_by_repo)  # {'2025-09-01', ...}
streaks = compute_streaks(dates, until_iso[:10])
total_commits = sum(len(v) for v in commits_by_repo.values())
badges = assign_badges(streaks, total_commits)

render_streaks(streaks)
render_badges(badges)

stale = detect_stale_repos(filtered_repos, threshold_days)
render_stale_nudges(stale, limit=5)
```

Streak computation sketch:
```
# activity_dates: set('YYYY-MM-DD')
cur = 0; longest = 0; last_active = None
cursor = date.fromisoformat(until)
while cursor.isoformat() in activity_dates:
  cur += 1; last_active = cursor.isoformat(); cursor -= 1 day

# longest: scan sorted dates and count contiguous runs
run = 0; prev = None
for d in sorted(activity_dates):
  if prev and date.fromisoformat(d) == date.fromisoformat(prev) + 1 day:
    run += 1
  else:
    longest = max(longest, run)
    run = 1
  prev = d
longest = max(longest, run)
return StreakStats(cur, longest, last_active)
```

## Acceptance Criteria
- With commit data present, the UI shows current and longest streaks; zero/sparse data yields clear empty states.
- At least three badges appear appropriately based on rules; no badge when criteria not met.
- Stale repos list shows up to 5 repos exceeding threshold, sorted by days since last push; each entry includes repo name, days stale, and link.
- No additional GitHub API endpoints beyond existing ones; API calls remain bounded by `max_repos` and time window.

## Manual Test Plan
1) Run the app with typical filters and a 90-day window; verify streak and badges render.
2) Adjust `max_repos` to 5 and 20; verify performance remains acceptable and badges/streaks update.
3) Change “Stale Threshold (days)” to 7 and 60; verify the nudge list updates and sorting is correct.
4) Test with very few commits: ensure current streak is small or zero, badges adapt, and empty-state messages appear.
5) Open a repo recently updated; verify it disappears from stale list when threshold increases.

## Notes
- Author identity is not enforced; “activity” represents any commits in owned repositories within the window.
- Badges are intentionally simple for MVP and can be extended in later phases.

