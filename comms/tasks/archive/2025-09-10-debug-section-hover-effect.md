Title: Debug Section-wide Header Hover Effect

Intent:
- Add a `console.log` statement to the `MutationObserver` to debug why the section-wide hover effect is not working.

Target:
- Route(s): /
- Component(s): ui/components.py

Run: streamlit run app.py

Scope: markup allowed

References:
- comms/ui/reference/ui_changes_003.png

Acceptance Criteria:
- A `console.log` statement is added to the `MutationObserver` callback in `ui/components.py`.
- The application must run without errors.

Constraints:
- This is a temporary debugging step. The `console.log` statement should be removed once the issue is identified.
