# Code Cleanup Plan

Purpose: Guide safe, incremental code housekeeping without changing behavior. We proceed slowly, request approval before edits, and verify after each change.

Principles
- Small, reversible steps; no functional changes without explicit approval.
- Prefer clarity and consistency; avoid style churn.
- Keep UI/UX output unchanged while tidying.
- Document each action and candidates for later.

Session 2025-09-10
- Change: Consolidate duplicate import from `services.cache` in `app.py` into a single grouped import.
  - Before: two separate imports (one solely for `cached_fetch_next_steps`).
  - After: one grouped import including `cached_fetch_next_steps`.
  - Risk: None (no runtime behavior change).
  - Status: Applied.

- Change: Normalize import order at top of `app.py` (stdlib → third‑party → local; alphabetical within groups).
  - Before: Mixed ordering and a separate grouped import.
  - After: Ordered, grouped imports for clarity; no symbols added/removed.
  - Risk: None (organizational only).
  - Status: Applied.

- Change: Extract CSS/JS injection from `app.py` into `ui/components.py` helpers.
  - Before: Two large `st.markdown` blocks (CSS and header Deploy hider) inline in `app.py`.
  - After: New `inject_global_styles()` and `inject_header_deploy_hider()` in `ui/components.py`; `app.py` calls these helpers.
  - Risk: Very low (content unchanged; only relocation). 
  - Status: Applied.

- Change: Move `get_logo_base64()` from `app.py` to `ui/components.py` and import it in `app.py`.
  - Before: Helper defined inline in `app.py`.
  - After: `ui.components.get_logo_base64()` used from `app.py` for title logo; implementation unchanged.
  - Risk: Very low (pure relocation).
  - Status: Applied.

Immediate Observations (candidates, not yet changed)
- app.py
  - Large inline CSS/JS blocks inside `main()`; consider moving to a small helper in a later step for readability once we’re confident. No behavior change planned yet.
  - `main()` is long; later we can extract clearly bounded sections (filters, repo table, visualizations, next steps, motivation, nudges) one at a time.
- UI styles
  - Fonts/CSS are imported in multiple places (Bebas Neue in `ui/components.py`; JetBrains Mono/Crimson Text in `app.py`). Later, we might centralize imports to one place to avoid duplication.
- Analytics/time handling
  - Consistent use of UTC and ISO8601 looks good; later we can add small helpers for date parsing to reduce repeated patterns.

Next Proposed Small Change (pending approval)
- Normalize import grouping across `app.py` top-of-file imports (sorting/grouping only; no adds/removes). Low risk, purely organizational.

Verification Notes
- After each change, run the app and quickly click through: load repos, filters, visualizations, NEXT_STEPS, motivation, nudges. Verify no visual or functional regressions.
