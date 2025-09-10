Title: Section-wide Header Hover via CSS :has() + Streamlit Containers

Intent:
- Hovering anywhere within a section should fully highlight its header, matching the on-title hover effect.
- Replace brittle JS/iframe hacks with a CSS-first approach anchored to Streamlit’s own container.
- Preserve accessibility: focus within the section should also activate the highlight; no UI jitter.

Target:
- Route(s): `/` (Streamlit app)
- Component(s): `ui/components.py` (ensure_section_header_styles), `app.py` (section grouping)

Run: AUTO

Scope: markup allowed (CSS-first; optional minimal JS fallback)

References:
- comms/2025-09-10-debug-hover-effect.md (context and prior attempts)
- Desired behavior shown in provided screenshot (Project Tasks highlighted when hovering section)

Acceptance Criteria:
- Hovering any area inside a section causes that section’s header background fill to animate to 100%; leaving the section reverts it.
- Keyboard focus anywhere inside the section also activates the header via focus-within.
- Implemented using CSS `:has()` on Streamlit’s block container: `[data-testid="stVerticalBlock"]:has(.gd-section-title):hover .gd-section-title` and `:focus-within` variant.
- No iframe script lifting or per-node JS listeners required. A tiny delegated JS fallback is included only if `CSS.supports('selector(:has(*))')` returns false.
- Works consistently on all five sections: Visualizations, Project Tasks, Task List Viewer, Motivation, and Nudges.

Changes:
1) Group headers with content using Streamlit containers
   - In `app.py`, replace manual HTML wrappers (`st.markdown("<div class='gd-section-wrap'>" ...)`) with:
     ```python
     with st.container():
         render_section_header("…", level='h2', accent='…')
         # section content…
     ```
   - Ensure each section’s header and its content live in the same container block.

2) CSS :has()-based hover activation (primary path)
   - In `ensure_section_header_styles()` (ui/components.py), append rules:
     - `[data-testid="stVerticalBlock"]:has(.gd-section-title):hover .gd-section-title { background-size: 100% 100%; }`
     - `[data-testid="stVerticalBlock"]:has(.gd-section-title):focus-within .gd-section-title { background-size: 100% 100%; }`
   - Keep existing header hover/focus styles for direct interaction.

3) Remove brittle wrappers and iframe lifting
   - Delete any reliance on `.gd-section-wrap` for hover activation in CSS.
   - Remove the iframe “lift” script and MutationObserver hover setup from `ensure_section_header_styles()`.

4) Progressive enhancement fallback (only if needed)
   - If `:has()` is unsupported, inject one delegated listener on `document.body` that, on `mouseover`/`focusin`, finds the closest `[data-testid="stVerticalBlock"]` containing a `.gd-section-title` and toggles `data-gd-active` on that title; clear it on `mouseout`/`focusout`.
   - Add `.gd-section-title[data-gd-active="true"] { background-size: 100% 100%; }` to CSS (already present, keep).

Viewports:
- 1440×900 (desktop), 390×844 (mobile)

Constraints:
- No new dependencies; reuse existing CSS injection via `st.markdown`.
- Do not change header typography/spacing.
- Keep `render_section_header` API unchanged.

Notes:
- `[data-testid="stVerticalBlock"]` is the Streamlit container used for block grouping; using it with `:has()` ties hover to the true ancestor that survives rerenders.
- Our primary browser (Brave/Chromium) supports `:has()`; fallback covers older engines if needed.

