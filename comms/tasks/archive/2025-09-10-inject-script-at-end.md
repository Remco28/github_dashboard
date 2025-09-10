Title: Inject Hover Effect Script at End of Body

Intent:
- Inject the hover effect script at the end of the `main()` function in `app.py` to ensure it runs after all other content has been rendered. This is a debugging step to confirm if the script is being executed at all.

Target:
- Route(s): /
- Component(s): app.py, ui/components.py

Run: streamlit run app.py

Scope: markup allowed

Acceptance Criteria:
- The `ensure_section_header_styles` function in `ui/components.py` should be modified to only contain the CSS styles. The `<script>` tag should be removed.
- A new `st.markdown` call should be added at the end of the `main()` function in `app.py` to inject the JavaScript.
- The JavaScript should be simplified to a single `console.log('Script executed');` statement for debugging purposes.
- The application must run without errors.

Constraints:
- This is a temporary debugging step.
