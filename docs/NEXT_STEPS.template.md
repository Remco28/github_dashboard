---
title: NEXT_STEPS Template
description: Recommended structure for repository task lists consumed by the dashboard.
---

# NEXT STEPS

Use this checklist to track follow-up items for the repository. The dashboard looks for this file at `comms/NEXT_STEPS.md` (preferred) and falls back to the repository root if needed.

## How to Use

1. Create a `comms/` directory at the root of your repository.
2. Copy this template to `comms/NEXT_STEPS.md`.
3. Organize tasks under headings (`#`, `##`, or `###`) and mark them with `- [ ]` (open) or `- [x]` (done).
4. Keep descriptions concise; the dashboard will display them grouped by section.

## Example Structure

```markdown
# NEXT STEPS

## Planning
- [ ] Draft Q4 roadmap
- [x] Review backlog with stakeholders

## Implementation
- [ ] Refactor cache layer for new requirements
- [ ] Add error telemetry to notifications panel

## Follow Up
- [x] Schedule sprint review demo
- [ ] Prepare release notes draft
```

## Tips

- Keep headings short; the UI uses them as section titles.
- Use checkboxes only (`- [ ]` or `- [x]`) so parsing remains predictable.
- If you need to temporarily stay with the root-level `NEXT_STEPS.md`, the dashboard will still ingest it, but plan to migrate to the `comms/` directory for consistency.
