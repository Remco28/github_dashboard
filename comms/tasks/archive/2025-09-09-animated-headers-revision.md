# UI Revision: Section Headers (Top Rule + Full Hover Fill, No Emojis, All Sections)

## Summary
Refine the new animated section headers to match the desired behavior:
- Show a thin colored line ABOVE the text by default.
- On hover/focus, the entire text background fills with that color.
- Remove emojis from section titles.
- Apply the header component consistently to sections: Visualizations, Project Tasks, Task List Viewer, Motivation, and Nudges — each with a distinct accent color.

## Issues Observed
- The colored line currently renders below the text.
- On hover, only ~half the text area fills due to the gradient stop at 60% transparency.
- Emojis still appear (e.g., 📊).
- Some sections (Task List Viewer, Motivation, Nudges) do not use the new header effect yet.

## Changes Required
1) Update header CSS for top rule + full fill
   - File: `ui/components.py` → `ensure_section_header_styles()`
   - Replace the current gradient logic with a solid-color background that animates from a 3–4px top rule to a full fill.
   - CSS requirements:
     - `.gd-section-title { background-image: linear-gradient(var(--gd-accent, #ffd54f), var(--gd-accent, #ffd54f)); background-repeat: no-repeat; background-position: 0 0; background-size: 100% 4px; transition: background-size .45s ease; }`
     - On hover/focus-visible: `background-size: 100% 100%;`
     - Keep focus ring and reduced-motion rules. With reduced motion, remove transitions; the fill can still appear instantly on hover/focus.
     - Prefer `display: inline` or `inline-block` to keep the fill bounded to the text; retain slight bottom padding and small radius for aesthetics.

2) Add accent options
   - In addition to existing `gold`, `blue`, and `green`, add:
     - `.gd-accent-red { --gd-accent: #ef9a9a; }`
     - `.gd-accent-purple { --gd-accent: #b39ddb; }` (optional if needed for better differentiation)

3) Remove emojis from section titles and apply headers to all sections
   - File: `app.py`
   - Replace usages:
     - Visualizations: `render_section_header("Visualizations", level='h2', accent='blue')` (remove icon)
     - Project Tasks: `render_section_header("Project Tasks", level='h2', accent='gold')`
     - Task List Viewer: replace `st.subheader("📋 Task List Viewer")` with `render_section_header("Task List Viewer", level='h3', accent='green')`
     - Motivation: replace `st.header("🏆 Motivation")` with `render_section_header("Motivation", level='h2', accent='purple')` (or `green` if purple not added)
     - Nudges: replace `st.header("🚨 Nudges")` with `render_section_header("Nudges", level='h2', accent='red')`

4) Keep imports consistent
   - Ensure `from ui/components import render_section_header` exists and is not duplicated; remove any now-unused icon args.

## Pseudocode (CSS excerpt)
```
.gd-section-title {
  display: inline;
  font-weight: 700;
  line-height: 1.15;
  padding-bottom: 2px;
  border-radius: 4px;
  background-image: linear-gradient(var(--gd-accent, #ffd54f), var(--gd-accent, #ffd54f));
  background-repeat: no-repeat;
  background-position: 0 0; /* top */
  background-size: 100% 4px; /* thin top rule */
  transition: background-size .45s ease;
}
.gd-section-title:hover, .gd-section-title:focus-visible {
  background-size: 100% 100%; /* full fill */
}
.gd-accent-red { --gd-accent: #ef9a9a; }
.gd-accent-purple { --gd-accent: #b39ddb; }
@media (prefers-reduced-motion: reduce) {
  .gd-section-title { transition: none; }
}
```

## Acceptance Criteria
- The default state shows a thin colored line above the text for each section header.
- Hovering/focusing fully fills the text background with the section’s color (no partial fill).
- Visualizations, Project Tasks, Task List Viewer, Motivation, and Nudges all use the new header component.
- No emojis remain in these section titles.
- Each section has a distinct accent color.
- No layout shifts or interference with the sidebar toggle/menu hiding.

## Test Plan
1) Verify default top rule appears for each targeted section.
2) Hover and focus via keyboard; confirm full background fill and visible focus ring.
3) Confirm no emojis present; titles render cleanly.
4) Check reduced-motion setting: the fill appears without animation (instant change).
5) Confirm all five sections use distinct accent colors and are applied in the intended locations.

## Notes / Rollback
- If wrap occurs on narrow widths, the fill will cover wrapped lines as intended.
- Rollback by reverting to the previous gradient rules and original `st.header`/`st.subheader` calls.

