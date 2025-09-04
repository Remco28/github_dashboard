# NEXT STEPS – GitHub Project Tracker Dashboard

This repository’s working checklist for near-term improvements and polish.

## UI/UX Polish
- [ ] Tune spacing/line-height for long markdown sections
- [ ] Improve table column widths and wrapping for long repo names

## Performance & Robustness
- [ ] Add optional per-section refresh buttons
- [ ] Add lightweight telemetry counters (local only) for cache hits/misses
- [x] Unify cache stats banner copy and expiration display

## Filters & Time Window
- [ ] Support activity windows beyond 365 days (e.g., 730 days)
- [ ] Consider an "All time" option with clear rate-limit guidance

## Project Tasks (NEXT_STEPS)
- [x] Add a root-level NEXT_STEPS.md for dogfooding
- [ ] Add “Repos without NEXT_STEPS.md” quick create guidance

## Nudges
- [ ] Refine stale repo detection thresholds and messaging tone
- [ ] Add "Snooze for 7 days" control to hide a nudge temporarily
- [ ] Cap and sort stale list by most inactive first; add "last active" date
- [ ] Place nudges panel consistently under summary cards

## Stretch
- [ ] Optional: export aggregated NEXT_STEPS tasks as CSV

## Rollout
- [ ] Add NEXT_STEPS.md files to other repos (Owner task)

---

Notes:
- Keep the file in the repository root so the app can fetch it via the GitHub Contents API.
- Use `- [ ]` and `- [x]` checkboxes under headings; the parser recognizes H1–H3 section headers.
