# Polish: Header Controls + Slider Value Clipping + Image Width Deprecation

## Summary
After the sidebar toggle regression fix, two UI regressions remain:
1) The Streamlit "Deploy" and main menu (three dots) show again for some Streamlit versions.
2) The "Activity Window (days)" slider’s value appears visually clipped to "36" instead of "365" in the sidebar at certain widths.
Additionally, a deprecation warning appears for `use_container_width` on images.

## Scope
- File: `app.py`
- Optional: no changes to business logic; CSS only, plus image width arg update.

## Root Cause Analysis
- The current CSS hides `[data-testid="stMenu"]` and `[data-testid="stDeployButton"]` which does not cover some Streamlit variants where different attributes/classes are used for these controls.
- Sidebar slider value clipping occurs due to tight right padding in the sidebar container at narrow widths, causing the numeric badge to be partially outside the visible area.
- `st.sidebar.image(..., use_container_width=True)` triggers a console deprecation in modern Streamlit; the supported API is `width='stretch'`.

## Changes Required
1) Robustly hide header menu/deploy without affecting the sidebar toggle
   - Keep existing rules and add safe fallbacks that target the controls themselves, not parent containers:
     - `.stDeployButton { display: none !important; }` (class fallback)
     - `header button[title*="Deploy" i] { display: none !important; }` (title hint)
     - `header [aria-label*="menu" i] { display: none !important; }` (main menu fallback)
     - `header [data-testid*="Menu" i] { display: none !important; }` (variant testid)
   - Explicitly do NOT hide `[data-testid="stSidebarCollapseButton"]` or any header ancestors.

2) Prevent slider value clipping in the sidebar
   - Add modest right padding to sidebar’s block container only:
     - `.stSidebar .block-container { padding-right: 10px !important; }`
   - Avoid altering `.stApp` margins or the global header height.

3) Address image width deprecation
   - Replace `use_container_width=True` with `width='stretch'` for `st.sidebar.image`.

## Implementation Notes (Pseudocode)
```
# In app.py, update the CSS block to add:
<style>
  /* Existing rules remain */
  [data-testid='stMenu'], [data-testid='stDeployButton'] { display:none !important; }

  /* Fallbacks for various Streamlit versions */
  .stDeployButton { display:none !important; }
  header button[title*='Deploy' i] { display:none !important; }
  header [aria-label*='menu' i] { display:none !important; }
  header [data-testid*='Menu' i] { display:none !important; }

  /* Sidebar padding to avoid clipping */
  .stSidebar .block-container { padding-right: 10px !important; }
</style>

# Replace image arg:
st.sidebar.image("media/remco28_github.png", width='stretch')
```

## Acceptance Criteria
- "Deploy" control and the three‑dot main menu are hidden across tested Streamlit versions without impacting the sidebar toggle.
- "Activity Window (days)" slider shows full values (e.g., 365) with no visual clipping at typical desktop widths and when the sidebar is collapsed then expanded.
- No console deprecation warnings for `use_container_width`.
- No overlap or loss of interactivity in the header/toggle.

## Test Plan
1) Launch app; confirm three dots menu and deploy control are hidden.
2) Collapse and expand sidebar; confirm toggle remains visible and functional.
3) Resize window narrower; verify the slider value (e.g., 365) is fully readable; adjust the value and confirm display.
4) Check browser console; verify no `use_container_width` warnings.

## Risks & Rollback
- Selector variance: If a future Streamlit header changes attributes, only cosmetic hiding may regress; functionality remains.
- Rollback: Remove or comment the new CSS rules if any unintended header element is hidden.
