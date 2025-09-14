# NEXT STEPS – GitHub Repository Dashboard

This repository’s working checklist for near-term improvements and polish.

## Appearance Tweaks

- [x] Add better distinction for sections.
- [x] Section header hover coverage: keep the title highlighted when hovering anywhere within the section content. Consider explicit `st.container()` wrappers per section and a reliable mapping between headers and content blocks.
- [x] Remove extra horizontal rules
- [x] Remove the cache stats bar. Hide it until we reveal it? Make a toggle with description "🤓"
- [x] Add text shadows to stats text
- [x] Make badges narrower
- [ ] Remove lingering inline styles from Achievements badges; use `.gd-badge(s)` CSS only

## Filters & Time Window

- [ ] Support activity windows beyond 365 days (e.g., 730 days)
- [ ] Consider an "All time" option with clear rate-limit guidance

## Project Tasks (NEXT_STEPS)

- [x] Add a root-level NEXT_STEPS.md for dogfooding
- [x] Add “Repos without NEXT_STEPS.md” quick create guidance

## Rollout

- [x] Add NEXT_STEPS.md files to other repos (Owner task)

---

Notes:

- Keep the file in the repository root so the app can fetch it via the GitHub Contents API.
- Use `- [ ]` and `- [x]` checkboxes under headings; the parser recognizes H1–H3 section headers.
