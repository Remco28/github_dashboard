# UI Touchups: Header Thickness, Padding, and Section-Wide Hover Activation

## Summary
Polish the new section headers per feedback:
- Make the colored top rule thicker (approximately 2× the current thickness).
- Add horizontal padding so the highlight extends slightly before and after the text.
- Activate the highlight when the user hovers anywhere within the section, not just on the title, so the section title remains highlighted while interacting inside that section.

## Scope
- Files: `ui/components.py`, optionally `app.py` for minimal grouping if needed.
- Components: CSS adjustments and a lightweight JS enhancer to link each header to its containing section block.

## Changes Required
1) Increase top rule thickness and add horizontal padding
   - File: `ui/components.py` → `ensure_section_header_styles()`
   - Update `.gd-section-title` CSS:
     - Increase rule height from `4px` to `8px` (2× current).
     - Add horizontal padding for pre/post highlight, e.g., `padding: 0 8px 2px;` (8px left/right, 2px bottom to balance aesthetics).
     - Keep the solid color fill approach and rounded corners.
   - Resulting key declarations:
     - `background-image: linear-gradient(var(--gd-accent), var(--gd-accent));`
     - `background-position: 0 0;`
     - `background-size: 100% 8px;`
     - `padding: 0 8px 2px;`

2) Section-wide hover activation
   - Add CSS so hovering the section container also triggers the fill:
     - `.gd-section-wrap:hover .gd-section-title { background-size: 100% 100%; }`
   - Add a tiny JS enhancer, executed once, that:
     - Finds each `.gd-section-title` and locates its closest Streamlit block container (e.g., `div[data-testid="stVerticalBlock"]`).
     - Adds a `gd-section-wrap` class to that container if not present.
     - Optionally attaches `mouseenter`/`mouseleave` listeners to set a `data-gd-active` attribute on the title (fallback), though `:hover` on the wrap is sufficient.
   - Implementation note: Use a MutationObserver to tag headers rendered after initial load.

3) Optional grouping (only if hover area is too small)
   - If a section’s content is not within the same block as its header, wrap the section in a Streamlit container to ensure a proper hover area:
     - `with st.container():`
       - `render_section_header(...)`
       - section content ...
   - Do not over-nest; apply only if needed.

## Pseudocode
```python
# ensure_section_header_styles() additions/changes
.gd-section-title {
  display: inline;
  font-weight: 700;
  line-height: 1.15;
  padding: 0 8px 2px;              /* extend color before/after text */
  border-radius: 4px;
  background-image: linear-gradient(var(--gd-accent), var(--gd-accent));
  background-repeat: no-repeat;
  background-position: 0 0;        /* top */
  background-size: 100% 8px;       /* thicker top rule */
  transition: background-size .45s ease;
}
.gd-section-title:hover, .gd-section-title:focus-visible,
.gd-section-wrap:hover .gd-section-title,
.gd-section-title[data-gd-active="true"] {
  background-size: 100% 100%;      /* full fill */
}

# One-time JS injected alongside the CSS (new ensure_section_header_behavior() or inline in styles injector)
(function(){
  if (window._gdHeaderEnhancerLoaded) return; window._gdHeaderEnhancerLoaded = true;
  const tagWrap = el => {
    try {
      const block = el.closest('div[data-testid="stVerticalBlock"], section.main, div.block-container');
      if (block && !block.classList.contains('gd-section-wrap')) block.classList.add('gd-section-wrap');
    } catch(_) {}
  };
  const scan = () => document.querySelectorAll('.gd-section-title').forEach(el => tagWrap(el));
  const mo = new MutationObserver(scan); mo.observe(document.body, {childList:true, subtree:true});
  document.addEventListener('DOMContentLoaded', scan); scan();
})();
```

## Acceptance Criteria
- The default top rule is visibly thicker (~8px) above the text.
- The highlight extends slightly before and after the word due to horizontal padding.
- Hovering anywhere in the section (not only over the title) causes the title highlight to fill completely.
- Existing accessibility remains: focus-visible ring; reduced-motion removes animation transitions.
- No regressions to header/toggle behavior or other styles.

## Test Plan
1) Inspect Visualizations header: confirm thicker top rule and pre/post highlight padding.
2) Move mouse anywhere in the Visualizations section content: the title should remain highlighted.
3) Repeat for Project Tasks, Task List Viewer, Motivation, and Nudges.
4) Tab to headers: focus ring appears; fill activates.
5) Enable reduced-motion at OS level: transitions are removed; state changes still occur.

## Notes
- If any section’s hover area doesn’t activate, group the header and its content inside a `st.container()` as noted.
- Keep colors from prior spec; no emoji changes needed (already removed).

