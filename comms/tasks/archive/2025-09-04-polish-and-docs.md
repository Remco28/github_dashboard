# Phase 7 – Polish & Docs

## Goal
Improve usability and onboarding so a new user can set up the app and see charts within 10 minutes. Add a user-facing theme toggle and a sidebar Settings Help panel. Ship clear README docs and screenshots.

## Scope
- In: Theming toggle (light/dark), Settings Help panel, README with Quickstart/Troubleshooting, screenshots, confirm `.env.example` guidance.
- Out: Deployment guides (Phase 8), new data features, large UI redesigns.

## Files and Targets
- `app.py`
  - Add an "Appearance" sidebar section with a theme selector.
  - Insert a "Settings Help" expander in the sidebar using a new helper.
- `ui/components.py`
  - Add: `render_theme_toggle()` to render and return selected theme.
  - Add: `apply_theme(theme: str)` to inject CSS for light/dark.
  - Add: `render_settings_help(username: str)` to show config guidance and redacted token tips.
- `README.md`
  - Create/Update with Overview, Features, Quickstart, Configuration, Running, Troubleshooting, Screenshots, Roadmap pointers.
- `docs/screenshots/`
  - Add PNGs: `dashboard.png`, `visualizations.png`, `next_steps.png`.
- `.env.example`
  - Verify comments are sufficient; keep keys as `GITHUB_TOKEN`, `GITHUB_USERNAME`.

## Detailed Requirements
1) Appearance / Theme Toggle
   - Location: Sidebar, under Filters but above Cache Controls.
   - Control: `selectbox` with options `Auto`, `Light`, `Dark`.
   - Behavior:
     - Persist selection in `st.session_state['theme']`.
     - Call `apply_theme(theme)` on every run; when set to `Auto`, do not inject custom CSS.
     - Minimum: background/text colors switch for Streamlit containers; content remains readable in both modes.
     - Charts: not required to change templates in this phase (optional enhancement).

2) Settings Help Panel
   - Location: Sidebar, below Cache Controls (after cache stats).
   - Control: `st.expander("Settings Help")` containing guidance and a summary.
   - Content (non-sensitive):
     - Show the configured GitHub username (from `get_settings()`), if available.
     - Do NOT display the token; include a note that it is loaded from env and must have appropriate scopes (`repo` for private, `public_repo` for public-only).
     - Link or mention `.env.example`. Provide 3–4 bullets for common setup pitfalls (missing token, wrong scopes, rate limits).

3) README
   - Sections:
     - Overview (what the app does) and feature bullets (repos table, charts, NEXT_STEPS, streaks/badges, cache controls).
     - Quickstart: create venv (optional), `pip install -r requirements.txt`, set `.env`, run `streamlit run app.py`.
     - Configuration: explain `GITHUB_TOKEN` and `GITHUB_USERNAME`, token scopes, `.env` placement, `.gitignore` note.
     - Troubleshooting: Authentication errors, Rate limit messaging, Empty states, Cache controls.
     - Screenshots: embed `docs/screenshots/*.png`.
     - Roadmap/Architecture links: `docs/ROADMAP.md`, `docs/ARCHITECTURE.md`.

4) Screenshots
   - Capture and save PNGs to `docs/screenshots/`:
     - `dashboard.png`: Top of app with stat cards and table.
     - `visualizations.png`: Language pie + commits charts.
     - `next_steps.png`: NEXT_STEPS aggregate and repo details.
   - Ensure images are <1MB each.

## Acceptance Criteria
- Theme toggle appears in sidebar and switches between at least Light and Dark styles with readable text and backgrounds. Selection persists during the session.
- Settings Help expander appears in sidebar, shows the configured username, never prints token, and includes actionable setup tips.
- `README.md` exists with the required sections and accurate instructions; a new user can set up and see charts within 10 minutes following it.
- `docs/screenshots/dashboard.png`, `docs/screenshots/visualizations.png`, and `docs/screenshots/next_steps.png` exist and are referenced in README.
- `.env.example` remains present with the two keys and explanatory comments.

## Constraints
- Do not leak secrets in UI, logs, or screenshots.
- Keep changes minimal; do not refactor chart functions for theming in this phase.
- Maintain existing coding style and module boundaries.

## Guidance / Pseudocode
- `ui/components.py` additions:
  - `def render_theme_toggle() -> str:`
    - `theme = st.sidebar.selectbox("Appearance", ["Auto", "Light", "Dark"], index=0, help="Choose dashboard theme")`
    - `st.session_state["theme"] = theme`
    - `return theme`
  - `def apply_theme(theme: str) -> None:`
    - If theme == "Dark": inject CSS via `st.markdown("""<style> ... </style>""", unsafe_allow_html=True)` to set page background to dark and text to light.
    - If theme == "Light": inject complementary light CSS (or clear by injecting minimal overrides).
    - If theme == "Auto": no-op (rely on Streamlit default).
  - `def render_settings_help(username: str) -> None:`
    - With `st.sidebar.expander("Settings Help")`:
      - `st.write(f"GitHub Username: **{username or 'Not set'}**")`
      - `st.write("Token: loaded from environment (not displayed)")`
      - Bullet list of setup steps and common fixes (scopes, rate limits, cache bypass).

- `app.py` integration (high-level):
  - After sidebar Filters are created and before Cache Controls:
    - `from ui.components import render_theme_toggle, apply_theme, render_settings_help`
    - `selected_theme = render_theme_toggle()`
    - `apply_theme(selected_theme)`
  - After cache stats rendering, call: `render_settings_help(settings.github_username)`

## Risks & Notes
- CSS injection affects only basic styling; Plotly theme alignment can be added later.
- Keep accessibility in mind (contrast ratios). Use readable colors for metrics and table text.

