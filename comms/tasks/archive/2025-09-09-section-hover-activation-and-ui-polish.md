# UI Polish: Section-Wide Hover Activation, Streaks Bar Removal, Badge Styling, Circular Progress

## Summary
Address four UX improvements:
1) Make the animated section header highlight activate when hovering anywhere within the section (not only on the title).
2) Remove the weekly/current streak progress bar from the Activity Streaks area.
3) Style Achievements badges with a subtle bordered “badge card” look.
4) Replace linear progress bars in the Task List Viewer with circular progress indicators showing the percentage in the center.

## Scope
- Files: `ui/components.py`, `app.py`, `ui/gamification.py`, `ui/checklists.py`
- No changes to data fetching or business logic.

---

## 1) Section-Wide Hover Activation (Animated Headers)

### Problem
Hovering within a section does not highlight the section header, despite the intended effect.

### Approach
Implement robust, JS-assisted activation that toggles a data attribute on the corresponding header when the section container is hovered or focused. Keep CSS fallback that reacts to `.gd-section-wrap:hover`.

### Changes
- File: `ui/components.py` (in `ensure_section_header_styles()`)
  - Ensure the CSS includes:
    - `.gd-section-wrap:hover .gd-section-title { background-size: 100% 100%; }`
    - `.gd-section-title[data-gd-active="true"] { background-size: 100% 100%; }`

- File: `ui/components.py` (new helper inside the same injector, or a sibling function called once):
  - Add a one-time JS snippet that:
    1. Finds each `.gd-section-title` element.
    2. Locates the nearest Streamlit block container (query selectors to try in order):
       - `div[data-testid="stVerticalBlock"]`
       - `div.block-container`
       - fallback to `el.parentElement` walk up to 5 levels
    3. Adds class `gd-section-wrap` to that container (for CSS :hover path).
    4. Attaches `mouseenter` and `mouseleave` listeners on that container to set/unset `data-gd-active="true"` on the specific header span.
    5. Uses a `MutationObserver` to apply the same logic for newly rendered headers.

- File: `app.py` (only if needed)
  - If any section does not share a container block with its content (rare), wrap the header and content in `with st.container():` to ensure a coherent hover region.

### Acceptance
- Hovering anywhere inside a section causes the corresponding title to fully highlight.
- Keyboard focus within the section also keeps the highlight (mouse leave ends only when focus leaves the section).
- No regressions to header/menu/toggle behavior.

---

## 2) Remove Weekly/Current Streak Progress Bar

### Changes
- File: `ui/gamification.py` → `render_streaks`
  - Remove the `st.progress(...)` visualization entirely.
  - Keep metrics (Current Streak, Longest Streak, Last Active) and status messages.

### Acceptance
- No progress bar is shown in Activity Streaks.
- Metrics and messages remain intact.

---

## 3) Achievements: Badge Card Styling

### Goal
Give badges a “real badge” feel: subtle border, rounded corners, gentle background, slight elevation; emoji centered with label.

### Changes
- File: `ui/gamification.py`
  - Add `ensure_badge_styles()` that injects CSS once:
    - `.gd-badges { display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 12px; }`
    - `.gd-badge { display: flex; flex-direction: column; align-items: center; justify-content: center; padding: 10px 12px; border: 1px solid rgba(0,0,0,0.08); border-radius: 10px; background: linear-gradient(180deg, #fff, #fafafa); box-shadow: 0 1px 2px rgba(0,0,0,0.04); }`
    - `.gd-badge-emoji { font-size: 28px; line-height: 1; margin-bottom: 6px; }`
    - `.gd-badge-label { font-weight: 600; text-align: center; font-size: 13px; }`
  - Update `render_badges(badges)` to:
    - Call `ensure_badge_styles()` once.
    - Render a single HTML grid (`.gd-badges`) of `.gd-badge` items via `st.markdown(..., unsafe_allow_html=True)` instead of multiple `st.metric` calls, to allow the styled card look.
    - Each card shows emoji div, then label div; use `title` attribute for tooltip description.

### Acceptance
- Badges appear as tidy cards with a subtle border, rounded corners, and slight elevation.
- Emoji and label are centered; layout is responsive across widths.
- Tooltip still available via hover (`title` attribute).

---

## 4) Task List Viewer: Circular Progress Indicator

### Goal
Replace linear `st.progress` bars with circular progress showing the percentage centered.

### Approach
Use Plotly to render a compact donut chart (pie with hole) per progress instance.

### Changes
- File: `ui/components.py` (or `ui/checklists.py`) — add helper:
  - `render_progress_circle(percent: int, *, size: int = 90, thickness: int = 10, color: str = "#64b5f6") -> None`
    - Builds a donut with two slices: `percent` and `100 - percent`.
    - Styles the chart: no axes, no legend, fixed size (`size` x `size`), hole radius computed from `thickness`.
    - Overlays the percentage text centered using Plotly annotations.
- File: `ui/checklists.py`
  - Replace `st.progress(progress, text=...)` usages:
    - Aggregate per-repo row: show the circular indicator in `col_progress` with the percent in the center; keep counts in `col_count`.
    - Single repo view (`render_repo_next_steps`): show the circular indicator instead of linear bar; percent in the center.

### Acceptance
- Circular progress appears where progress bars used to be, with centered percentage.
- Sizing fits neatly in list rows and single-repo section without overflow.
- No additional legends or axes are visible; charts are responsive.

---

## Test Plan
1) Section hover: hover anywhere within each section (Visualizations, Project Tasks, Task List Viewer, Motivation, Nudges) and confirm the title fills.
2) Streaks: confirm the weekly/current progress bar is gone; metrics remain.
3) Badges: verify new card styling, hover shows description tooltip, layout wraps nicely at smaller widths.
4) Task List Viewer: confirm circular progress with centered percentage in both aggregate per-repo rows and the single repo view.

## Risks & Rollback
- Section hover depends on DOM structure; the JS enhancer and observer should make it robust. If issues arise, temporarily disable section-wide activation by removing the listener logic.
- For badges and circular progress, fall back to the prior `st.metric` and `st.progress` if rendering issues are observed.

