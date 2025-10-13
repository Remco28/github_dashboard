# Spec: Priority 2 – Repo Table Usability Enhancements

**Date:** 2025-10-13  
**Author:** Architect  
**Status:** READY  
**Priority:** 2 (Major Usability Enhancements)

## 1. Objective
- Make the repository table the control center for catching up on activity by adding an inline name filter and richer pull-request visibility while relying on Streamlit’s built-in column sorting.
- Surface open pull requests (including items awaiting the user’s review) alongside the existing repository metadata without overwhelming the layout.

## 2. Background
- Priority 1 removed gamification clutter and added a useful “Last Push” column, but the table is still static once filters are applied in the sidebar.
- Product owners want Priority 2 to deliver meaningful interactivity and actionable data directly in the table. Today there is no inline filter, users must rely on the sidebar search, and PR activity is absent.
- The dashboard already fetches repositories via `services/github_client.list_user_repos` and caches results. We will build on that flow and reuse the existing cache/refresh controls.

## 3. Scope
**In Scope**
- Move the repository name search experience into the main content area and ensure the resulting filter is applied consistently across the table and downstream analytics.
- Preserve and document the Streamlit-native column sorting experience so users can order the table without extra UI chrome.
- Fetch open pull request metadata, compute counts, and show both the total open PRs and how many are waiting on the signed-in user’s review (with visual emphasis).
- Gracefully handle API failures and rate limits without crashing the page.

**Out of Scope**
- Server-side pagination or infinite scroll.
- Adding new GitHub data beyond open pull requests (e.g., closed PRs, reviews history).
- Persisting user-defined sort/filter presets across sessions.
- UI redesign beyond the table controls and new columns.

## 4. User Stories
- *As a maintainer*, I can quickly filter the repository table by typing part of a repo name so that I can focus on one project without losing the rest of the dashboard context.
- *As a reviewer*, I can scan which repositories have open pull requests and immediately spot any that are waiting on my review, so I know where to spend my time.
- *As a power user*, I can click table headers to sort by the signal I care about (e.g., most open PRs or latest push) without exporting data.

## 5. Deliverables
- Updated repository filtering flow inside `app.py` that captures the inline table search query and shares it with existing analytics.
- Extended models in `models/github_types.py` to hold pull-request counts (total + awaiting review) without breaking existing code.
- New GitHub client helper and cache wrapper for listing open pull requests (`services/github_client.py`, `services/cache.py`).
- Pull-request enrichment helper in `services/analytics.py` that annotates repositories prior to rendering.
- Enhanced table UI in `ui/tables.py` with:
  - Inline “Filter by name” text input surfaced directly above the Repository Details section.
  - New “Open PRs” and “Needs Review” columns (sortable, with styling for review-needed).
  - Updated column config to preserve relative-date formatting for Last Push.
- Updated acceptance guidance in this spec only; no documentation changes are required elsewhere for this task.

## 6. Technical Plan

### 6.1 Models (`models/github_types.py`)
- Extend `RepoSummary` with pull-request metadata fields placed after existing required fields:
  - `open_pr_count: int = 0`
  - `needs_review_pr_count: int = 0`
  - `needs_review_urls: tuple[str, ...] = field(default_factory=tuple)`
- Ensure defaults are provided so existing `to_repo_summary` calls remain valid; import `field` from `dataclasses`.
- Document (via brief comment) that `needs_review_urls` stores canonical PR links for tooltip/hover use only.

### 6.2 GitHub Client & Cache (`services/github_client.py`, `services/cache.py`)
- Add `list_repo_pull_requests(owner: str, repo: str, token: str, state: str = "open") -> list[dict]`:
  - Reuse `_request_with_retry`, paginate via `parse_next_link`, request up to 100 items per page.
  - Include request params: `state=open`, `per_page=100`, `sort=updated`, `direction=desc`.
  - The returned JSON must contain at least: `html_url`, `title`, `user.login`, `draft`, `requested_reviewers`, `requested_teams`, `updated_at`.
  - Catch `NotFoundError` similarly to other helpers and return `[]` if repo access is lost.
- Add `cached_list_repo_pull_requests` in `services/cache.py` with a 5-minute TTL and `cache_bust` support mirroring `cached_list_repo_commits`.

### 6.3 Pull-Request Enrichment (`services/analytics.py`)
- Implement `attach_pull_request_metadata(repos: list[RepoSummary], token: str, username: str, cache_bust: str | None = None) -> list[RepoSummary]`:
  - Import `cached_list_repo_pull_requests` lazily inside the function to avoid circular dependencies.
  - For each repo, derive `owner`, `name` from `repo.full_name`.
  - Fetch open PRs; treat failures (`RateLimitError`, network issues) by logging via `st.warning` in the caller (see below) and leaving counts at zero.
  - Count total open PRs excluding drafts (`draft is False`) so numbers reflect actionable work.
  - Determine review-needed PRs by checking case-insensitive match of `username` against `requested_reviewers[].login`. (Teams: safe to ignore for now; note in code comment.)
  - Populate the new fields on the `RepoSummary` instance and include canonical `html_url` values for review-needed PRs in `needs_review_urls`.
  - Return the mutated list so the caller can continue chaining.

### 6.4 App Orchestration (`app.py`)
- Remove the sidebar `st.text_input("Search", ...)` block; the sidebar filters become language/visibility/activity only.
- Immediately after computing `all_repo_summaries`, but before rendering stat cards, create a main-content container that introduces the table controls:
  - Place the inline `st.text_input` labeled “Filter repositories by name” directly above the “Repository Details” heading; store its value in `table_filter_query`.
  - Optionally show a concise helper text reminding users that table headers remain clickable for sorting.
- Apply filters:
  - Call `filter_repos(..., query=table_filter_query.strip() or None)` so all downstream sections (stats, charts, NEXT_STEPS) respect the inline search.
  - Call the new `attach_pull_request_metadata` with the filtered list before any UI rendering; propagate `cache_bust` so the Refresh button forces PR refetches.
- Keep a single `filtered_repos` list and pass it to both `render_stat_cards` and the table; rely on `st.dataframe` interactive sorting for ordering.
- Handle enrichment errors gracefully: if `attach_pull_request_metadata` raises, catch in `main()` and show a callout (`render_section_error` or `st.warning`) while continuing with zeroed PR data.

### 6.5 Table Rendering (`ui/tables.py`)
- Add a small control header inside `render_repo_table` (or a new helper called beforehand) to surface the inline filter summary back to the user (e.g., “Filtered by: ‘foo’”).
- Update dataframe construction:
  - Include `repo.open_pr_count` and `repo.needs_review_pr_count`.
  - Keep the existing UTC-aware datetime object for `Last Push` so pandas sorting remains correct.
  - If `needs_review_pr_count > 0`, include a Markdown-formatted bullet list string of links in a hidden column (e.g., `_Review Links`) for tooltips.
- Update styling:
  - Continue using `df.style.format({"Last Push": format_relative_date})`.
  - Apply a style function that highlights the “Needs Review” cell (e.g., bold text + warning background) when the value is > 0.
- Update `st.dataframe` configuration:
  - Add `Open PRs` as `st.column_config.NumberColumn` with `format="%d"` and a tooltip clarifying drafts are excluded.
  - Add `Needs Review` as `NumberColumn` with a tooltip explaining the highlight and link behavior.
  - Optionally add a `st.column_config.TextColumn` for `_Review Links` with `help` only, then mark it hidden via `column_order`/`column_config` so it can be used for hover or future expansion.
  - Adjust `column_order` to place PR columns near issues (e.g., `["Name", "Private", "Open PRs", "Needs Review", "Open Issues", ...]`).
- Document (inline comment) that `st.dataframe` provides per-column sorting via the header menu, so no additional sorting UI is required.

### 6.6 Error Handling & Refresh
- Ensure the existing “Refresh” button and `bypass_cache` checkbox pass `cache_bust` into both repo and PR fetches so users can force an updated count.
- When PR data fails to load due to rate limiting, show a single warning banner near the table (use `render_section_error` or `st.warning`) and fall back to zeros; do not break the rest of the dashboard.

## 7. Testing & QA Guidance
- **Unit Tests**
  - Add `tests/test_pull_requests.py` covering `attach_pull_request_metadata` logic with mocked PR payloads:
    - Scenario: multiple PRs with drafts and requested reviewers; assert counts and URLs.
    - Scenario: user name casing differences (e.g., username uppercase) still matches.
    - Scenario: API failure path returns original repo list with zero counts.
  - Update existing tests if they instantiate `RepoSummary` so defaults for the new fields are validated.
- **Manual QA**
  - Run the app with sample data; confirm inline filter narrows all KPI counts and downstream sections.
  - Verify default sort (Open PRs desc, Last Push desc, Name asc) and that changing controls reorders the table deterministically.
  - Trigger the Refresh button and ensure PR counts update.
  - Simulate API failure (e.g., temporary network block) to ensure warning appears and page continues rendering.

## 8. Acceptance Criteria
- Inline name filter is visible in the main content area, synced with all downstream analytics, and survives reruns without jumping focus.
- Users can sort by any column directly through the Streamlit dataframe UI (verify the header menu offers ascending/descending options).
- The table shows two new numeric columns: “Open PRs” and “Needs Review”. Columns are sortable, and cells with review-required counts > 0 are visibly highlighted.
- Pull-request counts exclude drafts and update when the Refresh button is used (or cache is bypassed).
- When the GitHub API returns an error or hits rate limits, the dashboard displays a non-blocking warning and defaults PR counts to zero.
- No regressions: existing filters (language, visibility, activity) and NEXT_STEPS processing continue to function.

## 9. Open Questions / Follow-Ups
- Future enhancements could surface direct links or hover cards for review-needed PRs; for now we only show counts.
- Team review requests are ignored until we have a reliable way to map teams to the authenticated user; document this in code comments for future handling.
- Consider caching the inline filter selection in session state across tabs in a later iteration if users request it.
