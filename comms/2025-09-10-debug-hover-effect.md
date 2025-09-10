# Debugging the Section-wide Header Hover Effect

## Problem

The hover effect on the section headers is not being triggered when hovering over the section content.

## Attempted Solutions

1.  **Initial Implementation:** Wrapped sections in `gd-section-wrap` divs and used JavaScript to add event listeners.
    *   **Result:** Failed. The script ran before the content was loaded.

2.  **MutationObserver:** Introduced a `MutationObserver` to detect when the sections were added to the DOM.
    *   **Result:** Failed. The script was not being re-executed on page updates.

3.  **Force Re-injection:** Removed the `st.session_state` check to force the script to be re-injected on every page update.
    *   **Result:** Failed. No console output.

4.  **Inject at End of Body:** Moved the script injection to the end of the `main()` function in `app.py`.
    *   **Result:** Failed. No console output.

5.  **Lift Script out of Iframe:** Used `st.components.v1.html` to inject the script and then "lift" it out of the `iframe` into the main document.
    *   **Result:** Partially successful. The script was lifted and executed in the parent document, but the hover effect still did not work.

6.  **Debug with Visual Cue:** Added a visual cue (a red border) to the hover effect to debug whether the event listeners are being attached correctly.
    *   **Result:** Pending.

## Findings (Designer Lead)

- Streamlit block boundaries prevent custom wrappers from enclosing section content. Each widget/header renders inside its own `[data-testid="stVerticalBlock"]`; an `st.markdown("<div class='gd-section-wrap'>")` cannot span subsequent widgets. As a result, `.gd-section-wrap` never actually contained the charts/cards, so `:hover` on it did not represent the whole section.
- Listener-based approaches were brittle because Streamlit frequently rerenders and replaces nodes; attaching listeners to ephemeral wrappers or relying on a local iframe context was unreliable. Lifting the script to the parent document executed, but still targeted the wrong container (the custom wrapper, not the true Streamlit block).
- Root cause: wrong hover anchor. We need to anchor hover/focus state to the real Streamlit container that wraps the header and its content.

## Recommended Approach

1) Group header + content using Streamlit containers
   - Use `with st.container():` so the header and all section content live in the same Streamlit block.

2) CSS-first hover using :has() on Streamlit’s container
   - Add rules in `ensure_section_header_styles()`:
     - `[data-testid="stVerticalBlock"]:has(.gd-section-title):hover .gd-section-title { background-size: 100% 100%; }`
     - `[data-testid="stVerticalBlock"]:has(.gd-section-title):focus-within .gd-section-title { background-size: 100% 100%; }`
   - Keep existing direct hover/focus styles on `.gd-section-title`.

3) Remove iframe/MutationObserver hover enhancer
   - No per-node listeners are required for the primary path. If needed for older browsers, gate a tiny delegated fallback behind `CSS.supports('selector(:has(*))')` that toggles `data-gd-active` on the title of the closest `[data-testid="stVerticalBlock"]`.

## Browser Support Note

- `:has()` is supported in Chromium-based browsers (e.g., Brave/Chrome) and Safari; this matches our dev environment in the screenshot. A minimal fallback covers non-supporting engines.

## Next Steps

- Implement spec at `comms/tasks/2025-09-10-section-hover-via-has-and-container.md`:
  - Replace manual HTML wrappers with `st.container()` per section.
  - Add the `:has()` rules; remove the iframe “lift” script and related observers.
  - Verify all five sections (Visualizations, Project Tasks, Task List Viewer, Motivation, Nudges) respond to hover and focus-within.

## Outcome

- Status: Resolved. The developer implemented the CSS `:has()` solution with `st.container()` grouping and the refined “deepest-only” selector. Hovering within a section now highlights only that section’s header. Keyboard focus within a section also activates the header as expected. No iframe/observer scripts are required.
- Notes: If additional nested headers are introduced later, ensure they live in separate `st.container()` blocks to preserve the deepest-only behavior.
