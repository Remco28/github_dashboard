# NEXT STEPS – GitHub Project Tracker Dashboard

This repository’s working checklist for near-term improvements and polish.

## UI/UX Polish
- [ ] Improve dark mode readability (inputs, tables, links, charts)
- [ ] Align Plotly charts with theme toggle
- [ ] Tune spacing/line-height for long markdown sections

## Performance & Robustness
- [ ] Add optional per-section refresh buttons
- [ ] Add lightweight telemetry counters (local only) for cache hits/misses
- [x] Unify cache stats banner copy and expiration display

## NEXT_STEPS Integration
- [x] Add a root-level NEXT_STEPS.md for dogfooding
- [ ] Add “Repos without NEXT_STEPS.md” quick create guidance

## Stretch
- [ ] Optional: dark theme for Plotly with a custom palette
- [ ] Optional: export aggregated NEXT_STEPS tasks as CSV

---

Notes:
- Keep the file in the repository root so the app can fetch it via the GitHub Contents API.
- Use `- [ ]` and `- [x]` checkboxes under headings; the parser recognizes H1–H3 section headers.

