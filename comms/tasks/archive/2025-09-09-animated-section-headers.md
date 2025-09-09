# UI: Animated Section Headers (Gradient Highlight)

## Summary
Introduce a reusable, accessible section header component that provides a modern animated highlight effect inspired by the sample design (gradient background that grows on hover). Replace plain `st.header(...)` calls in the main page with this component for clear, scannable section boundaries that feel consistent with our UI polish.

No external font is required; we’ll rely on system fonts. The effect uses pure CSS and does not change business logic.

## User Stories
- As a user, I can quickly recognize major sections (Visualizations, Project Tasks) thanks to distinctive, consistent headers.
- As a keyboard user, focusing a section header reveals the same highlight affordance as hover, aiding navigation.
- As a user who prefers reduced motion, I don’t experience distracting animation; the highlight appears without transition.

## Scope
- Files: `ui/components.py`, `app.py`
- Components: New `render_section_header(...)` helper and a one-time global style injector.
- Out of scope: Data fetching, caching, chart logic, NEXT_STEPS parsing, gamification.

## Design Notes
- The example uses absolute positioning; we will not. Our headers sit in normal flow.
- Effect: A background gradient underlines the text by default (subtle); on hover/focus it expands to a full highlight fill.
- Accessibility: Respect `prefers-reduced-motion`; support keyboard focus via `tabindex` and `:focus-visible` styling.
- Theming: Provide a small set of accent classes (e.g., gold, blue, green) the caller can choose per section.

## Changes Required
1) Add a reusable section header component
   - File: `ui/components.py`
   - New functions:
     - `ensure_section_header_styles() -> None`
       - Inject a `<style>` block only once (guard with `st.session_state`), defining `.gd-section`, `.gd-section-title`, accent classes, and reduced-motion rules.
     - `render_section_header(title: str, icon: str | None = None, *, level: str = 'h2', accent: str = 'gold', align: str = 'left') -> None`
       - Renders semantic header markup using `st.markdown(..., unsafe_allow_html=True)`, e.g.:
         - `<h2 class="gd-section" style="text-align: left;">` + `<span class="gd-section-title gd-accent-gold" tabindex="0">📊 Visualizations</span>` + `</h2>`
       - Valid `level`: `'h2' | 'h3'` (default `'h2'`).
       - Valid `accent`: `'gold' | 'blue' | 'green'` (default `'gold'`).
       - Valid `align`: `'left' | 'center'` (default `'left'`).
       - Calls `ensure_section_header_styles()` on first use.

   - CSS (inject via `ensure_section_header_styles`):
     - Container spacing:
       - `.gd-section { margin: 16px 0 8px; }`
     - Title effect:
       - `.gd-section-title { display: inline; font-weight: 700; line-height: 1.1; padding-bottom: 2px; border-radius: 4px; background-repeat: no-repeat; background-position: 0 100%; background-size: 100% 0.35em; transition: background-size .5s ease, background-position .5s ease; }`
       - Background uses a CSS variable: `background-image: linear-gradient(0deg, transparent 60%, var(--gd-accent, #ffd54f) 60%);`
       - Hover/focus expand: `.gd-section-title:hover, .gd-section-title:focus-visible { background-size: 100% 100%; background-position: 0 0; }`
       - Focus ring: `.gd-section-title:focus-visible { outline: 2px solid var(--gd-accent, #ffd54f); outline-offset: 2px; }`
     - Accents:
       - `.gd-accent-gold { --gd-accent: #ffd54f; }`
       - `.gd-accent-blue { --gd-accent: #64b5f6; }`
       - `.gd-accent-green { --gd-accent: #81c784; }`
     - Reduced motion:
       - `@media (prefers-reduced-motion: reduce) { .gd-section-title { transition: none; } }`

   - Pseudocode:
     ```python
     def ensure_section_header_styles():
         if st.session_state.get('_gd_section_css_loaded'): return
         st.markdown("""
         <style>
           .gd-section { margin: 16px 0 8px; }
           .gd-section-title { display:inline; font-weight:700; line-height:1.1; padding-bottom:2px; border-radius:4px; background-image:linear-gradient(0deg, transparent 60%, var(--gd-accent, #ffd54f) 60%); background-repeat:no-repeat; background-position:0 100%; background-size:100% 0.35em; transition: background-size .5s ease, background-position .5s ease; }
           .gd-section-title:hover, .gd-section-title:focus-visible { background-size:100% 100%; background-position:0 0; }
           .gd-section-title:focus-visible { outline:2px solid var(--gd-accent, #ffd54f); outline-offset:2px; }
           .gd-accent-gold { --gd-accent: #ffd54f; }
           .gd-accent-blue { --gd-accent: #64b5f6; }
           .gd-accent-green { --gd-accent: #81c784; }
           @media (prefers-reduced-motion: reduce) { .gd-section-title { transition:none; } }
         </style>
         """, unsafe_allow_html=True)
         st.session_state['_gd_section_css_loaded'] = True

     def render_section_header(title, icon=None, *, level='h2', accent='gold', align='left'):
         ensure_section_header_styles()
         safe_icon = (icon + ' ') if icon else ''
         cls = f"gd-section-title gd-accent-{accent}"
         tag = 'h2' if level == 'h2' else 'h3'
         st.markdown(
             f"<{tag} class='gd-section' style='text-align:{align};'><span class='{cls}' tabindex='0'>{safe_icon}{title}</span></{tag}>",
             unsafe_allow_html=True,
         )
     ```

2) Replace plain headers on the main page
   - File: `app.py`
   - Replace:
     - `st.header("📊 Visualizations")`
       with `render_section_header("Visualizations", icon="📊", level='h2', accent='blue')`.
     - `st.header("📝 Project Tasks")`
       with `render_section_header("Project Tasks", icon="📝", level='h2', accent='gold')`.
   - Import the helper at top: `from ui.components import render_section_header` (and ensure Python import ordering matches code style).
   - No change to `st.title(...)` for now; keep the page title as-is to avoid layout side effects. (Optional follow-up: style the title similarly if desired.)

3) Ensure styles load once
   - The helper self-injects styles on first render; no need to modify the large CSS block in `app.py`.
   - This avoids interference with existing header/menu/toggle fixes.

## Constraints
- Do not import external fonts or JS libraries.
- Keep selectors scoped to `.gd-*` to avoid conflicts with Streamlit internals.
- Maintain compatibility with the existing CSS that hides the deploy/menu controls.

## Acceptance Criteria
- Visualizations and Project Tasks sections render with the animated highlight header component.
- Hovering a header fills the highlight; keyboard focus shows the same effect with a visible focus ring.
- With `prefers-reduced-motion: reduce`, the header appears highlighted without animation.
- No layout shift, overlap, or regression of the sidebar toggle/menu-hiding behavior.
- No console errors or warnings in the browser.

## Test Plan
1) Load the app and confirm both sections render with the new headers.
2) Hover over each header and observe the background fill animation.
3) Navigate via keyboard (Tab) to the header; verify the focus ring and fill appear.
4) Simulate reduced motion (OS setting) and reload; verify no animation.
5) Collapse/expand the sidebar and resize the window; verify headers remain intact and readable.
6) Verify the Deploy/menu controls remain hidden per existing CSS; no accidental hiding of the sidebar toggle.

## Risks & Rollback
- If any styling conflict is observed, revert calls to `render_section_header` back to `st.header(...)` and remove the style injector.
- Scoped `.gd-*` classes minimize the risk of affecting other elements.

## Developer Notes
- Follow the import and formatting conventions used elsewhere (e.g., import grouping in `app.py`).
- Keep the helper generic for future sections; only Visualizations and Project Tasks are in scope for this change.
- If Streamlit sanitizes spans differently in future releases, switch to a `<div role="heading" aria-level="2">` wrapper while preserving semantics.

