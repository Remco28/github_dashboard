Title: Section-wide Header Hover Effect

Intent:
- When a user hovers their mouse anywhere within a content section, the corresponding section header should display its hover effect. This provides a clear visual cue of the user's context.

Target:
- Route(s): /
- Component(s): app.py, ui/components.py

Run: streamlit run app.py

Scope: markup allowed

References:
- comms/ui/reference/ui_changes_003.png

Acceptance Criteria:
- Hovering the mouse over the content of the "Visualizations", "Project Tasks", "Task List Viewer", "Motivation", or "Nudges" sections triggers the hover animation on the respective section's header.
- The hover effect is removed when the mouse leaves the section.
- The existing JavaScript that tries to find section containers and add the `gd-section-wrap` class should be removed from `ui/components.py`.
- In `app.py`, each section should be explicitly wrapped in a container that has the `gd-section-wrap` class. The most reliable way to do this is to use `st.markdown("<div class='gd-section-wrap'>", unsafe_allow_html=True)` to open the div before the section content and `st.markdown("</div>", unsafe_allow_html=True)` to close it after.

Constraints:
- Reuse existing classes/tokens; no new dependencies unless explicitly allowed.
