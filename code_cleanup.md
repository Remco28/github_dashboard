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

Session 2025-09-11
- Change: Remove unused `base64` import from `app.py`.
  - Before: `import base64` remained after moving logo encoding to `ui/components.py`.
  - After: Unused import removed.
  - Risk: None (no runtime behavior change).
  - Status: Applied.

- Change: Normalize import grouping in `ui/components.py` (stdlib → third‑party → local; alphabetical within groups).
  - Before: Third‑party and local imports came before stdlib; order inconsistent.
  - After: Groups reordered to `base64` (stdlib), then `pandas`, `plotly`, `streamlit` (third‑party), then `models.github_types` (local). No symbols added/removed.
  - Risk: None (organizational only).
  - Status: Applied.

Additional Changes (same session)
- Change: Split UI helpers into focused modules for cohesion.
  - Moved `inject_global_styles()` and `inject_header_deploy_hider()` from `ui/components.py` to `ui/styles.py`.
  - Moved `get_logo_base64()` to new `ui/branding.py` and added `render_app_title()`.
  - Updated `app.py` to import from `ui.styles` and call `ui.branding.render_app_title()`; removed inline title HTML block.
  - Kept transitional re‑exports in `ui/components.py` to avoid breakage; no behavior change.
  - Risk: None (pure relocation; identical markup/styles).
  - Status: Applied.

Additional Changes (same session)
- Change: Extract section header helpers to dedicated module.
  - Moved `ensure_section_header_styles()` and `render_section_header()` from `ui/components.py` to `ui/headers.py`.
  - Updated `app.py` to import `render_section_header` from `ui.headers`.
  - Added transitional re‑exports in `ui/components.py` for header helpers.
  - Risk: None (pure relocation; identical CSS/JS and API).
  - Status: Applied.

Additional Changes (same session)
- Change: Move repo table and metrics helpers into dedicated modules.
  - Moved `render_repo_table` to `ui/tables.py`.
  - Moved `render_stat_cards` and `render_progress_circle` to `ui/metrics.py`.
  - Updated `app.py` to import from these modules; added transitional re‑exports in `ui/components.py`.
  - Risk: None (pure relocation; identical UI).
  - Status: Applied.

Next Proposed Small Change (pending approval)
- Decide on deprecating `ui/components.py` after callers are updated, or keep it as a thin façade. If deprecating, switch remaining imports in `app.py` and remove re‑exports in a later session.
