# Sidebar Toggle for Cache Stats

## Objective
Hide cache telemetry by default and expose it via a compact sidebar toggle labeled with a nerd emoji (🤓) and a tooltip "Display cache stats". When enabled, render the cache info panel in the sidebar under "💾 Cache Controls". When disabled, do not render any cache info in the main content or sidebar.

## User Stories
- As a user, I don’t want cache details cluttering the main view by default.
- As a power user, I can enable a small control to see cache stats on demand.

## Scope
- Add a sidebar control to show/hide cache stats (default: off).
- Move cache stats rendering into the sidebar and only render when enabled.
- Maintain existing cache functionality (bypass, clear, telemetry collection) unchanged.

## Files To Modify
- `app.py`
  - Location: Sidebar "💾 Cache Controls" section.
  - Add a toggle control for showing cache stats.
  - Condition rendering of cache stats on the toggle state.
  - Ensure cache info renders in the sidebar, not main content.
- `ui/notifications.py`
  - Function: `render_cache_info(cache_stats: dict)` → add optional location param.
  - New signature: `def render_cache_info(cache_stats: dict, location: str = "main") -> None`
  - Route output to `st.sidebar` when `location == "sidebar"`.

## Detailed Requirements
- Sidebar control
  - Primary: `st.sidebar.toggle("🤓", help="Display cache stats", key="show_cache_stats")`.
  - Back-compat: If `st.toggle` is unavailable, fall back to `st.sidebar.checkbox` with the same label/help/key.
  - Default state: `False` (hidden).
- Rendering behavior
  - Compute `stats = cache_stats()` and `telemetry = cache_metrics()`; merge as today.
  - If `show_cache_stats` is `True`, call `render_cache_info(merged_stats, location="sidebar")` directly beneath the toggle (inside the Cache Controls section).
  - If `False`, do not render any cache info panel anywhere.
- `render_cache_info` routing
  - Determine destination: `dst = st.sidebar if location == "sidebar" else st`.
  - Replace current `st.info(...)` calls with `dst.info(...)` (including the early return path for empty cache).
  - No change to the information content/formatting.
- Ordering in sidebar
  - Place the new toggle above the "🧹 Clear Cache" button or immediately below the section header (Architect’s preference: above clear button to keep related controls grouped).
- No changes to `services/cache.py` telemetry collection.

## Non-Goals
- Changing telemetry content or collection logic.
- Adding new CSS or JS.
- Persisting the toggle beyond Streamlit’s normal session behavior.

## Pseudocode
```python
# app.py (within Cache Controls section)
show_cache_stats = getattr(st.sidebar, "toggle", st.sidebar.checkbox)(
    "🤓", help="Display cache stats", key="show_cache_stats"
)

if st.sidebar.button("🧹 Clear Cache"):
    clear_cache()
    st.sidebar.success("Cache cleared!")
    st.rerun()

stats = cache_stats()
telemetry = cache_metrics()
merged_stats = {**stats, **telemetry}

if show_cache_stats:
    render_cache_info(merged_stats, location="sidebar")
```

```python
# ui/notifications.py
def render_cache_info(cache_stats: dict, location: str = "main") -> None:
    dst = st.sidebar if location == "sidebar" else st
    count = cache_stats.get("count", 0)
    if count == 0:
        dst.info("💾 Cache is empty")
        return
    # ... build info_text exactly as today ...
    dst.info(info_text)
```

## Acceptance Criteria
- Default run shows no cache info panel in the main area or sidebar.
- Sidebar shows a control labeled exactly `🤓` with tooltip "Display cache stats".
- Enabling the control displays the cache info panel in the sidebar under "💾 Cache Controls"; disabling hides it.
- The panel content remains identical to current (entries count, cached functions, expiry range, performance, top functions) and respects the empty-cache message.
- "Bypass Cache" and "🧹 Clear Cache" behaviors are unchanged.
- Works on environments without `st.toggle` (fallback to checkbox).

## QA / Test Plan
1. Launch the app with a populated cache (navigate charts once to create entries).
2. Verify no cache panel is visible anywhere by default.
3. Hover the `🤓` control and confirm tooltip text is "Display cache stats".
4. Enable the control → cache panel appears in the sidebar below the control; verify text and values.
5. Disable the control → panel disappears.
6. Click "🧹 Clear Cache" → observe success message and panel updates to "💾 Cache is empty" when control is enabled.
7. Toggle between checkbox fallback and toggle (if applicable) to confirm identical behavior.

## Rollout Notes
- No migrations or config changes.
- Docs: Optional note that cache telemetry is available under a sidebar toggle; no architecture changes required.

## Definition of Done
- All acceptance criteria pass locally.
- Architect review approved.

