# Task Spec: NEXT_STEPS Integration (Phase 4)

Author: Architect
Date: 2025-09-03
Status: SPEC READY

## Summary
Integrate per-repo NEXT_STEPS.md files into the dashboard. Fetch, parse, and display actionable tasks and milestones from each repository. Provide an aggregated view across repos and a repo detail panel with checklists. Parsing must be tolerant to format drift and missing files.

## Objectives
- Fetch `NEXT_STEPS.md` from the root of each repository via the GitHub Contents API.
- Parse Markdown sections and checkboxes into structured data.
- Render an aggregate summary (open vs completed tasks, per-repo counts) and a repo detail view with interactive checklists (read-only for MVP).
- Handle missing files gracefully with guidance to add the template.

## User Stories
- As a user, I can see how many NEXT_STEPS tasks I have open across all repos.
- As a user, I can view a repo’s NEXT_STEPS with sections and checkboxes rendered as a checklist.
- As a user, I get a friendly message when a repo lacks NEXT_STEPS.md and a link to the template.

## In Scope
- Contents fetch for `NEXT_STEPS.md` and decoding base64 content.
- Markdown parsing for checkboxes (`- [ ]`, `- [x]`) and section headings (H1–H3).
- Aggregate counts and simple progress indicators per repo.
- Streamlit UI for aggregate block and repo detail panel.

## Out of Scope (defer)
- Editing/saving tasks back to GitHub via API (future enhancement).
- YAML-based alternative format (consider later if Markdown proves limiting).

## Files and Functions

- `services/github_client.py` (update)
  - `def get_file_contents(owner: str, repo: str, path: str, token: str) -> dict | None:`
    - Calls `GET /repos/{owner}/{repo}/contents/{path}`. On 404, return None. On 2xx, return response JSON.

- `services/next_steps.py` (new)
  - `from dataclasses import dataclass`
  - `@dataclass class TaskItem:` fields: `text: str`, `checked: bool`, `section: str | None = None`
  - `@dataclass class NextStepsDoc:` fields: `repo_full_name: str`, `raw_markdown: str | None`, `tasks: list[TaskItem]`, `sections: list[str]`
  - `def fetch_next_steps(owner: str, repo: str, token: str) -> str | None:`
    - Uses `get_file_contents` for `NEXT_STEPS.md`. If present, decode `content` base64 to UTF-8. Return Markdown string or None.
  - `def parse_next_steps(md: str, repo_full_name: str) -> NextStepsDoc:`
    - Parses headings `^#{1,3} ` as sections; captures current section name.
    - Parses checkboxes lines matching `^\s*[-*] \[( |x|X)\] (.+)$` into TaskItem with section.
    - Returns NextStepsDoc with tasks and sections.
  - `def summarize_tasks(tasks: list[TaskItem]) -> tuple[int, int]:`
    - Returns `(open_count, done_count)`.

- `services/cache.py` (update)
  - Add `@ttl_cache(300)` wrappers:
    - `cached_get_file_contents(owner: str, repo: str, path: str, token: str) -> dict | None`
    - `cached_fetch_next_steps(owner: str, repo: str, token: str) -> str | None`

- `ui/checklists.py` (new)
  - `def render_aggregate(tasks_by_repo: dict[str, list[TaskItem]]) -> None:` shows totals and per-repo progress bars.
  - `def render_repo_next_steps(doc: NextStepsDoc) -> None:` renders sections with checklists (read-only) using `st.checkbox(disabled=True)`.

- `app.py` (update)
  - Add a new section “NEXT_STEPS” below Visualizations.
  - For the current filtered repo list, fetch docs for up to `N` repos (e.g., 20) to keep latency bounded.
  - Display aggregate totals and a selector to drill into one repo to see its checklist.
  - Provide an info box with a link to the template for repos without the file.

## API Endpoints
- `GET /repos/{owner}/{repo}/contents/NEXT_STEPS.md`
- Headers: `Authorization: token <PAT>`, `Accept: application/vnd.github+json`

## Constraints & Non‑functional Requirements
- Performance: Cap parallel fetches (sequential for MVP) and number of repos processed per render to keep UI snappy.
- Resilience: Treat 404 as “file missing”; do not spam errors. Timeouts ~10s with friendly UI messages.
- Security: Do not log tokens; avoid printing full content in logs.

## Pseudocode & Notes

Fetch + parse loop (bounded):
```
results = {}
for r in filtered_repos[:20]:
  owner, name = r.full_name.split('/', 1)
  md = cached_fetch_next_steps(owner, name, token)
  if md is None:
    continue
  doc = parse_next_steps(md, r.full_name)
  results[r.full_name] = doc.tasks
```

Regex parsing example:
```
section = None
for line in md.splitlines():
  if m := re.match(r"^(#{1,3})\s+(.*)$", line):
    section = m.group(2).strip()
    continue
  if m := re.match(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$", line):
    checked = m.group(1).lower() == 'x'
    text = m.group(2).strip()
    tasks.append(TaskItem(text=text, checked=checked, section=section))
```

Aggregate rendering idea:
```
open_total = sum(1 for t in all_tasks if not t.checked)
closed_total = sum(1 for t in all_tasks if t.checked)
# per-repo progress bars using st.progress(closed / (open+closed))
```

## Acceptance Criteria
- When repos have NEXT_STEPS.md, the app displays an aggregate total of open/closed tasks and per-repo counts.
- Selecting a repo shows its sections with read-only checkboxes reflecting task status.
- Repos without NEXT_STEPS.md show a clear hint to add the template (link to template in docs).
- Performance: With 20 repos, parsing completes quickly (<500ms after data fetched).
- Errors/404s do not crash the app; NEXT_STEPS UI still renders for repos with data.

## Manual Test Plan
1) Add `NEXT_STEPS.md` to 1–2 repos using the provided template; include a mix of checked/unchecked tasks and multiple sections.
2) Launch app; verify aggregate counts reflect the documents.
3) Use the repo selector to view a particular repo’s checklist; verify sections and checkbox states.
4) Filter to repos with and without NEXT_STEPS.md; verify missing-file messaging.
5) Temporarily break formatting (e.g., odd indentation) and verify parser still captures checkboxes where possible.

## Deliverables
- Implemented modules and UI as listed.
- No new dependencies; use Python stdlib (base64, re, dataclasses).
- Clear inline docstrings and type hints.

