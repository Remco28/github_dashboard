# UI Polish: Hide Deploy Button Reliably + Chart Cards Styling

## Summary
- The header "Deploy" control is still visible in some Streamlit builds; we need a robust, targeted hide that doesn’t affect the sidebar toggle.
- Charts visually blend together (white on white). Add card-like styling (border, rounded corners, padding, spacing) around Plotly charts to improve separation.

## Scope
- File: `app.py` (CSS only)
- No changes to data logic; minimal/no changes to Python chart code.

## Approach
1) Robustly hide the Deploy control without touching header ancestors or the sidebar toggle.
   Add safe, targeted CSS selectors covering common Streamlit variants:
   - Keep: `[data-testid="stDeployButton"] { display:none !important; }`
   - Add fallbacks:
     - `.stDeployButton { display:none !important; }`
     - `header button[title*="Deploy" i] { display:none !important; }`
     - `header [aria-label*="Deploy" i] { display:none !important; }`
     - `header a[href*="share.streamlit.io"] { display:none !important; }`
     - `header a[href*="deploy" i] { display:none !important; }`
     - (Optional, progressive) `header :has(> [aria-label*="Deploy" i]) { display:none !important; }` — only if tested and safe; do not hide ancestors of the sidebar toggle.

   Do NOT hide: `[data-testid="stSidebarCollapseButton"]` or any header container elements.

2) Add card styling to Plotly charts via CSS only (no Python refactor required):
   Target Plotly containers using their testid and element structure.
   - `[data-testid="stPlotlyChart"] {\n      border: 1px solid rgba(0,0,0,0.08);\n      border-radius: 10px;\n      background: #fff;\n      padding: 12px;\n      margin-bottom: 16px;\n    }`
   - Optional subtle elevation: `box-shadow: 0 1px 2px rgba(0,0,0,0.04);`

   This yields borders and spacing between charts without changing chart code. Rounded corners are applied to the container.

3) Sidebar slider clipping
   Ensure previous fix remains: `.stSidebar .block-container { padding-right: 10px !important; }` to keep values like "365" fully visible.

4) Image width deprecation
   Ensure `st.sidebar.image(..., width='stretch')` is used instead of `use_container_width` to remove console warnings.

## Implementation Details
- Update the existing CSS block in `app.py` to append the selectors above. Example:
```
<style>
  /* Existing hidden controls */
  [data-testid='stMenu'], [data-testid='stDeployButton'] { display:none !important; }

  /* Robust deploy hiding across versions */
  .stDeployButton { display:none !important; }
  header button[title*='Deploy' i] { display:none !important; }
  header [aria-label*='Deploy' i] { display:none !important; }
  header a[href*='share.streamlit.io'] { display:none !important; }
  header a[href*='deploy' i] { display:none !important; }

  /* Plotly chart cards */
  [data-testid='stPlotlyChart'] {
    border: 1px solid rgba(0,0,0,0.08);
    border-radius: 10px;
    background: #fff;
    padding: 12px;
    margin-bottom: 16px;
    box-shadow: 0 1px 2px rgba(0,0,0,0.04);
  }

  /* Sidebar tweaks */
  .stSidebar .block-container { padding-right: 10px !important; }
</style>
```

- Replace `st.sidebar.image("media/remco28_github.png", use_container_width=True)` with `width='stretch'`.

## Acceptance Criteria
- Deploy button is hidden across tested Streamlit versions; the three-dot menu remains hidden; the sidebar toggle remains visible and functional.
- Plotly charts display within card-like containers with borders, rounded corners, padding, and vertical spacing between charts.
- No console warnings related to `use_container_width`.
- No changes in chart data, interactivity, or performance.

## Test Plan
1) Launch the app; verify the Deploy control is not visible in the header (multiple refreshes and viewports).
2) Collapse and expand the sidebar; ensure the toggle remains visible and clickable.
3) Inspect charts in both columns; confirm they are visually separated with borders, rounded corners, and spacing.
4) Resize the window; ensure the Activity Window slider shows full values (e.g., 365) and that chart styling remains consistent.
5) Check browser console for any warnings or errors; confirm the `use_container_width` warning is gone.

## Risks & Notes
- Streamlit may change internal attributes; provided multiple targeted selectors minimize regressions while avoiding ancestor/container hiding.
- If one selector is too broad in a future version, remove that single line; functionality will not be impacted.
