# Plan: Feature Refocus + NEXT_STEPS → FEATURES

Owner: Tech Advisor (draft for Architect)
Date: 2026-01-31
Status: Draft for review

## Goal
Refocus the dashboard on high-signal repo insights and simplify maintenance by replacing the
NEXT_STEPS workflow with a lightweight FEATURES checklist, while keeping as much of the existing
infrastructure as possible.

## Summary of Decisions
- Remove low-value repo metrics from Repository Details: Open PRs, Needs Review, Stars, Forks.
- Default Trend Granularity to Weekly (not Daily).
- Replace NEXT_STEPS.md with FEATURES.md (less granular, more stable).
- Remove Repository Progress (currently tied to task completion).
- Remove Task List Viewer as a standalone feature.
- Remove Recent Activity section (GitHub user events feed).
- Reconfigure existing "tasks" infrastructure to support Features + per-repo feature progress.
- FEATURES.md location: `comms/FEATURES.md` (not repo root).
- Feature granularity: product-level features.
- Feature states: Delivered / Not Delivered via checked/unchecked items.

## Proposed Experience
- Features.md contains a short app description and a checklist of features.
- Each repository can show "Feature Progress" based on which features are delivered.
- The old Task List Viewer becomes a "Feature Details" view for the selected repo.

## Proposed Features.md Structure (draft)
- Short description of the app (2-4 sentences).
- Checklist of features (delivered or not).
- Optional grouping by category (Overview / Data / Visualizations / Ops).

Example (structure only):
1) App description paragraph
2) [ ] Feature A
3) [x] Feature B
4) [ ] Feature C

## Implementation Notes (for Architect)
- Keep the parsing + display pipeline if possible (swap NEXT_STEPS parser for FEATURES parser).
- Map existing "task completion" progress to "features delivered" progress.
- Reuse UI affordances for lists and per-repo detail, but rename to "Features".

## Open Questions
1) None (pending new input).

## Out of Scope (for now)
- Any new data sources beyond GitHub API.
- New complex task management features.
- Major UI redesign beyond renaming/removing sections.

## Acceptance Criteria (draft)
- Repository Details no longer shows Open PRs, Needs Review, Stars, Forks.
- Trend Granularity defaults to Weekly.
- NEXT_STEPS references are replaced with FEATURES in UI and docs.
- Repository Progress and Task List Viewer are removed or repurposed as Feature Progress/Details.
- Documentation updated to reflect the new feature model.
