Title: Section Hover — Activate Only the Deepest Section

Intent:
- Prevent multiple headers from highlighting simultaneously when hovering nested areas; only the closest/innermost section under the cursor should activate.

Target:
- Component: `ui/components.py` (ensure_section_header_styles)

Run: AUTO

Scope: style-only

Acceptance Criteria:
- Moving the mouse within the main area highlights exactly one header: the section that directly contains the hovered content.
- Hovering inside the Task List Viewer (h3) does NOT also highlight the parent Project Tasks (h2).
- Keyboard interactions mirror this behavior via focus-within.

Changes:
- Replace the broad `:has()` selector with a “deepest hovered block” variant:

```css
/* Only the deepest hovered Streamlit block that owns a header activates */
[data-testid="stVerticalBlock"]
  :is(:hover, :focus-within)
  :has(> [data-testid="stMarkdownContainer"] .gd-section-title)
  :not(:has([data-testid="stVerticalBlock"] :is(:hover, :focus-within) .gd-section-title))
  .gd-section-title {
  background-size: 100% 100%;
}
```

Notes:
- This narrows activation to the innermost `[data-testid="stVerticalBlock"]` that (1) is hovered or focused, (2) owns a header, and (3) does not contain any hovered/focused descendant block that also owns a header.
- Keep existing direct `.gd-section-title:hover` and `[data-gd-active]` rules unchanged.

