# Fix: Sidebar Toggle Permanently Hides Sidebar

## Summary
Clicking the Streamlit sidebar collapse icon hides the sidebar, but the toggle to re‑open it becomes inaccessible, leaving the sidebar permanently hidden. This is a regression introduced by recent look‑and‑feel tweaks in `app.py` that inject global CSS/JS targeting Streamlit header/toolbar elements.

## Scope
- File: `app.py`
- Components: Global CSS/JS injected via `st.markdown(..., unsafe_allow_html=True)`; header/toolbar/sidebar behavior only.
- Out of scope: Core data fetching, caching, charts, NEXT_STEPS, gamification logic.

## Root Cause Analysis
- The injected CSS and JS indiscriminately hide header/toolbar containers that host the sidebar collapse button.
  - JS hides `[data-testid="stToolbar"]`, and CSS hides `.stAppToolbar`; if the sidebar toggle is a descendant, it disappears once state changes.
  - Broad class rules (e.g., `.css-1v3fvcr`, `.css-1v0mb2l`) target ephemeral Streamlit classes and may unintentionally hide or break interactive controls.
  - Additional layout tweaks (negative margin on `.stApp`, header height overrides) risk overlaying or detaching the toggle from its hit area.
- Net effect: The initial toggle click collapses the sidebar, but the toggle then becomes hidden or non‑interactive, preventing expansion.

## Desired Behavior
- The sidebar collapse/expand toggle remains visible and clickable in both open and collapsed states.
- The Streamlit menu and deploy button remain hidden for a clean UI.
- No overlapping or non‑interactive header regions; normal keyboard/mouse interactivity is preserved.

## Changes Required
1. Remove unsafe header/toolbar hiding
   - Delete the inline `<script>` block that sets `display:none` on `[data-testid="stToolbar"]` (and other elements).
   - Remove CSS rule `.stAppToolbar { display: none !important; }`.
   - Do not hide any ancestor container of `[data-testid="stSidebarCollapseButton"]`.

2. Replace broad CSS with targeted selectors
   - Keep hiding only the explicit, stable testids:
     - `[data-testid="stMenu"] { display: none !important; }`
     - `[data-testid="stDeployButton"] { display: none !important; }`
   - Remove rules for ephemeral classes like `.css-1v3fvcr` and `.css-1v0mb2l`.
   - Remove or neutralize risky layout hacks:
     - Delete `.stApp { margin-top: -20px !important; }`.
     - Revert/soften header overrides; avoid shrinking header in a way that affects toggle hitbox.
     - If top spacing needs reduction, adjust only `.block-container { padding-top: <smaller value>; }`.

3. Ensure toggle visibility in all states
   - Keep a minimal rule to ensure toggle visibility without relying on parent overrides:
     - `[data-testid="stSidebarCollapseButton"] { visibility: visible !important; opacity: 1 !important; }`
   - Do not scope the visibility rule only inside `.stSidebar` (toggle may not live there when collapsed).

4. Minor cleanup
   - Replace `st.sidebar.image(..., width='stretch')` with `st.sidebar.image(..., use_container_width=True)` to avoid unsupported width usage.

## Implementation Notes (Pseudocode)
```
# In app.py, replace the current CSS/JS block with:
st.markdown(
    """
    <style>
      /* Hide Streamlit menu/deploy controls only */
      [data-testid='stMenu'],
      [data-testid='stDeployButton'] { display: none !important; }

      /* Optional: modest spacing tweaks, avoid header/tooling containers */
      .block-container { padding-top: 0.75rem !important; }

      /* Keep the sidebar toggle visible in all states */
      [data-testid='stSidebarCollapseButton'] {
        visibility: visible !important;
        opacity: 1 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)
# Remove the <script> that hid [data-testid='stToolbar'] and any CSS hiding .stAppToolbar, .stApp margin-top hacks, and .css-* rules.
```

## Acceptance Criteria
- Sidebar can be collapsed and expanded via the header toggle at all times.
- The collapse/expand control remains visible and clickable on desktop and narrow widths.
- Sidebar widgets remain interactive after multiple collapse/expand cycles.
- Streamlit menu/deploy controls remain hidden; no other header elements are unintentionally hidden.
- No console errors; no content overlap with the header.

## Test Plan
1. Launch app and verify toggle visibility with sidebar open.
2. Click to collapse sidebar; verify the toggle remains visible and clickable; expand again.
3. Resize window to narrow width; repeat steps 1–2.
4. Interact with several sidebar controls after re‑expanding (buttons, sliders, radios) to confirm interactivity.
5. Confirm menu/deploy controls are hidden, but header area remains.
6. Check browser console for errors.

## Risks & Rollback
- If future Streamlit versions change testids, only the cosmetic hiding may regress; the sidebar toggle will remain functional because we avoid hiding ancestor containers.
- Rollback by removing the entire custom CSS block if any unexpected behavior occurs.

## Notes / Other Findings
- The previous `width='stretch'` on `st.sidebar.image` is not a supported value and may lead to warnings; using `use_container_width=True` is preferred.
