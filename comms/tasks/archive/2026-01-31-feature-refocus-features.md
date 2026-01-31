# Spec: Feature Refocus + FEATURES.md Migration

Owner: Architect  
Date: 2026-01-31  
Status: SPEC READY

## Goal
Refocus the dashboard on high-signal insights by removing low-value metrics and the Recent Activity feed, and replace NEXT_STEPS with a simpler FEATURES checklist stored in `comms/FEATURES.md` for each repo.

## User Story
As a maintainer, I want a lightweight features checklist per repo that’s easy to update and easy to read at a glance, without task-level overhead or noisy activity feeds.

## Scope
### In Scope
- Replace NEXT_STEPS flow with FEATURES flow.
- Remove Recent Activity section entirely.
- Remove low-value Repository Details columns: Open PRs, Needs Review, Stars, Forks.
- Default Trend Granularity to Weekly.
- Rename UI sections to “Features” and “Feature Details”, and show per-repo feature progress.
- Update tests and docs to match the new model.

### Out of Scope
- Any new data source beyond GitHub API.
- New UI redesign outside of section renames/removals.

## Product Decisions
- `FEATURES.md` lives at `comms/FEATURES.md` within each repo.
- Feature items are product-level and tracked via markdown checkboxes.
- Feature states: Delivered (checked) / Not Delivered (unchecked).

## Functional Requirements
1. **FEATURES Fetching**
   - New fetch path: `comms/FEATURES.md` (no root fallback).
   - Reuse the existing “get file contents” pattern.
2. **Parsing**
   - Parse markdown headers (H1–H3) as optional sections.
   - Parse `- [ ]` / `- [x]` as feature items.
   - Preserve the raw markdown for “view raw” fallback.
3. **UI: Aggregate Features**
   - Section title: “Features”.
   - Show aggregate totals (Total / Open / Completed / Progress).
   - Show per-repo “Feature Progress” using the existing progress circles.
4. **UI: Feature Details**
   - Section title: “Feature Details”.
   - Repo selector with search (reuse existing UI).
   - Display features grouped by section with read-only checkboxes.
5. **Remove Recent Activity**
   - Remove the “Recent Activity” section from `app.py`.
   - Remove unused modules / cache wrappers tied only to this section.
6. **Repository Details Table**
   - Remove columns: Open PRs, Needs Review, Stars, Forks.
   - Remove any PR metadata enrichment and related API calls if unused.
7. **Trend Granularity Default**
   - Default to Weekly (no automatic switch based on activity window).

## Files to Update (Expected)
### Core
- `app.py`
- `services/next_steps.py` → replace with `services/features.py` (or rename logic)
- `services/cache.py` (remove unused PR/event caches if no longer used)
- `services/github_client.py` (remove user events and PR list calls if unused)
- `services/analytics.py` (remove PR enrichment if unused)
- `ui/checklists.py` (rename + text updates for FEATURES)
- `ui/activity_feed.py` (remove if unused)
- `ui/tables.py` (remove columns)
- `models/github_types.py` (remove PR-related fields if no longer needed)

### Tests
- `tests/test_next_steps.py` → update or rename to FEATURES tests

### Docs
- `README.md` (features list and section names)
- `docs/ARCHITECTURE.md` (replace NEXT_STEPS with FEATURES component)
- `docs/ROADMAP.md` (if any feature mentions need cleanup)
- `comms/FEATURES.md` (already added, verify wording)

## Acceptance Criteria
- “Recent Activity” section is gone from UI and code.
- Repository table no longer shows Open PRs, Needs Review, Stars, Forks.
- Trend Granularity defaults to Weekly.
- NEXT_STEPS references in UI and code are replaced by FEATURES.
- Features are read from `comms/FEATURES.md` per repo and rendered as checklists.
- Per-repo progress is shown under a “Feature Progress” label.
- All tests updated and passing.

## Notes / Guidance
- Keep parsing/UX simple; this is a lightweight checklist, not a task manager.
- Prefer removing unused code paths to reduce API calls and rate-limit pressure.
