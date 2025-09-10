Title: Section-wide Header Hover Effect (Fix)

Intent:
- When a user hovers their mouse anywhere within a content section, the corresponding section header should display its hover effect. This provides a clear visual cue of the user's context.

Target:
- Route(s): /
- Component(s): ui/components.py

Run: streamlit run app.py

Scope: markup allowed

References:
- comms/ui/reference/ui_changes_003.png

Acceptance Criteria:
- Hovering the mouse over the content of the "Visualizations", "Project Tasks", "Task List Viewer", "Motivation", or "Nudges" sections triggers the hover animation on the respective section's header.
- The hover effect is removed when the mouse leaves the section.
- The current JavaScript for section-wide hover activation in `ui/components.py` should be replaced with the new, robust version that uses a `MutationObserver`.

Constraints:
- Reuse existing classes/tokens; no new dependencies unless explicitly allowed.

Notes:
- The `MutationObserver` is necessary because Streamlit renders content dynamically. The observer will watch for new elements being added to the page and apply the hover effect to the sections as they appear.
