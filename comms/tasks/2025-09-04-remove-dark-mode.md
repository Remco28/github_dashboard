# Spec: Remove Dark Mode and Theme Toggle (Light-Only UI)

## Objective
Simplify the UI to a single, consistent light theme. Remove the Dark mode option and all custom CSS and template wiring so we don’t spend time tweaking colors. Keep the app readable and consistent using Streamlit’s default light theme and Plotly’s default template.

## Rationale
- Reduce maintenance and visual QA overhead.
- Avoid CSS/selector churn and cross-widget inconsistencies.
- Default Streamlit + Plotly light themes are adequate for our use case.

## Scope (In)
- Remove the Appearance/theme toggle from the sidebar.
- Remove dark-mode CSS injection and related variables.
- Remove Plotly template switching via `st.session_state["plotly_template"]`.
- Ensure charts render with a sane default (Plotly’s default).
- Update docs to remove references to theming and dark mode.
- Remove unused asset `darkmode.png` if not referenced elsewhere.

## Scope (Out)
- Replacing screenshots immediately (optional; do only if a screenshot explicitly shows the theme toggle).
- Adding a new custom light theme (we’ll stick to Streamlit defaults).

## Changes Required

1) `ui/components.py`
   - Remove `render_theme_toggle()` and `apply_theme()` definitions entirely.
   - Remove any session state keys used only for theming (e.g., `st.session_state["plotly_template"]`).

2) `app.py`
   - Remove imports: `render_theme_toggle`, `apply_theme` from `ui.components`.
   - Remove calls: `selected_theme = render_theme_toggle()` and `apply_theme(selected_theme)`.
   - Remove any sidebar headings/descriptions that reference “Appearance” or theme.

3) `ui/charts.py`
   - Remove reads of `st.session_state["plotly_template"]` and any `template=...` entries wired to session state.
   - Use Plotly’s default template (do not set `template` explicitly unless needed to fix a regression).

4) `README.md`
   - Remove references to the theme toggle and dark mode.
   - In “Cache Controls / Setup / Troubleshooting”, ensure no theme guidance remains.

5) `docs/DEPLOYMENT.md`
   - Remove the “Verify theme toggle” step and any theming references.

6) `docs/ARCHITECTURE.md`
   - Update the Development Guidelines note to remove mention of theming toggle.
   - Optional: add a single line clarifying we use the default Streamlit theme (light-only) for simplicity.

7) Assets
   - If `darkmode.png` is not referenced in docs or README post-edit, delete it from the repo.

## Acceptance Criteria
- Running `streamlit run app.py` shows no “Appearance”/theme section in the sidebar.
- No custom CSS is injected for theming; visual style follows Streamlit default (light).
- Charts render legibly with Plotly defaults; no runtime warnings or errors about missing `plotly_template` keys.
- `rg -n "render_theme_toggle|apply_theme|plotly_template|Appearance"` returns no matches in source (except possibly in archived specs).
- README and DEPLOYMENT contain no references to theming or dark mode.
- If `darkmode.png` is unused, it is removed from the repository.

## Risks & Mitigations
- Minor visual differences after removing CSS: mitigate by quick sanity check of inputs, tables, alerts, and charts in the light theme.
- Docs drift: ensure README/DEPLOYMENT are updated in the same PR.

## Verification Steps
1. Start the app locally; confirm sidebar no longer has theme controls.
2. Navigate through all sections; confirm no styling regressions hinder readability.
3. Confirm cache banner, tables, and notifications are readable and aligned with default styling.
4. Run `rg` searches per acceptance criteria to ensure removal.

## Notes
- Keep the change minimal and focused: do not refactor unrelated UI components.

