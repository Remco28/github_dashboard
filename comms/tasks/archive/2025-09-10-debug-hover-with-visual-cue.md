Title: Debug Hover Effect with Visual Cue

Intent:
- Add a visual cue (a red border) to the section when it's being hovered. This will help us determine if the event listeners are being attached correctly.

Target:
- Route(s): /
- Component(s): ui/components.py

Run: streamlit run app.py

Scope: markup allowed

Acceptance Criteria:
- The `setupHoverEffect` function in `ui/components.py` should be modified to add a red border to the section when it's being hovered.
- The application must run without errors.

Constraints:
- This is a temporary debugging step.
