Title: Lift Hover Effect Script out of Iframe

Intent:
- Inject the hover effect script using `st.components.v1.html` and then "lift" it out of the `iframe` into the main document. This will allow the script to see the entire DOM and correctly apply the hover effect to the section headers.

Target:
- Route(s): /
- Component(s): ui/components.py

Run: streamlit run app.py

Scope: markup allowed

Acceptance Criteria:
- The `ensure_section_header_styles` function in `ui/components.py` should be modified to use `st.components.v1.html` to inject the JavaScript.
- The JavaScript should be modified to:
    - Find the `iframe` that contains the script.
    - Move the script's content (the `MutationObserver` logic) into the parent document.
    - Remove the `iframe` itself.
- The hover effect should work as expected.
- The application must run without errors.

Constraints:
- This is a complex operation, so the JavaScript must be written carefully to avoid errors.
