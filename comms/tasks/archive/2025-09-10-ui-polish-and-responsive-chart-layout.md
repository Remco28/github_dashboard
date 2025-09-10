Title: UI Polish and Responsive Chart Layout

Intent:
- The sidebar search input is indistinct from its background. It should be clearly visible.
- The main content charts should be in a responsive grid, defaulting to 2 columns and stacking to 1 column on smaller screens.

Target:
- Route(s): /
- Component(s): app.py, ui/charts.py

Run: streamlit run app.py

Scope: markup allowed

References:
- comms/ui/reference/ui_changes_002.png

Acceptance Criteria:
- The "Search" input box in the sidebar must have a visible border and background, similar to the "Languages" dropdown.
- The charts in the "Visualizations" section must be displayed in a responsive grid. On wide screens, there should be two charts per row. On narrow screens, the charts should stack into a single column.
- The application must run without errors.
- The JavaScript for applying section containers and grid layouts should be removed from app.py.
- The `width='stretch'` parameter in `st.plotly_chart` calls in `ui/charts.py` should be replaced with `use_container_width=True`.
- The responsive chart layout in `app.py` should be implemented using `st.columns`.

Constraints:
- Reuse existing classes/tokens; no new dependencies unless explicitly allowed.
