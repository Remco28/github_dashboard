Title: Streamlit UI Learnings — General Guide to Section‑Level Effects

Purpose
- Provide reusable patterns for applying section‑level visual/interactive effects (hover, focus, active state, shadows, sticky headers, dimming others) to Streamlit apps in a way that survives rerenders and remains accessible.

Core Principles
- Group with Streamlit, not raw HTML: `st.markdown("<div>…")` cannot wrap widgets rendered later. Use `with st.container():`, `st.columns()`, and `st.expander()` to create true DOM groups.
- Anchor to stable containers: Streamlit renders each logical block inside `[data-testid="stVerticalBlock"]`. Use that as the ancestor for section‑level selectors instead of custom wrappers.
- CSS‑first, JS‑last: Prefer CSS for state propagation (`:has()`, `:focus-within`). Only add small, delegated JS fallbacks when absolutely required.
- Scope and performance: Constrain selectors to the smallest region you can (e.g., `.block-container [data-testid="stVerticalBlock"]`) to avoid unnecessary re‑evaluation cost of dynamic selectors like `:has()`.
- Accessibility by default: Mirror pointer behaviors with focus equivalents; respect `prefers-reduced-motion`.

Implementation Checklist
- Structure
  - Wrap each section’s header and content in `with st.container():` so they share the same block.
  - Give the header a recognizable class (example: `.ui-section-title`). If you render headings via Markdown, insert a `<span class="ui-section-title">` around the visible text.
- CSS injection
  - Inject global styles once near the top of your app (e.g., in a helper called from `render_section_header`). Use `st.markdown("<style>…</style>", unsafe_allow_html=True)`.
- Section‑level activation (hover/focus)
  - Base rule: `[data-testid="stVerticalBlock"]:has(.ui-section-title):hover .ui-section-title { … }`
  - Add focus variant: `:focus-within` to mirror keyboard interactions.
  - For nested sections, prefer “deepest‑only” gating to avoid multiple headers lighting up simultaneously:
    `[data-testid="stVerticalBlock"] :is(:hover, :focus-within) :has(> [data-testid="stMarkdownContainer"] .ui-section-title) :not(:has([data-testid="stVerticalBlock"] :is(:hover, :focus-within) .ui-section-title)) .ui-section-title { … }`
- Reduced motion
  - Wrap transitions in an `@media (prefers-reduced-motion: reduce)` block to disable animations when requested.
- Fallback (legacy browsers)
  - Gate with `if (!CSS.supports('selector(:has(*))')) { … }`.
  - Use a single delegated listener on `document.body` to set a `data-active` attribute on the closest `[data-testid="stVerticalBlock"]` (or directly on the title). Keep this logic tiny and idempotent.

Common Effects (drop‑in examples)
- Hover/focus highlight for headers
  - `.ui-section-title { transition: background-size .35s ease; background-image: linear-gradient(var(--accent, #ffd54f), var(--accent, #ffd54f)); background-size: 100% 6px; background-repeat: no-repeat; background-position: 0 0; }`
  - Apply the deepest‑only rule to grow `background-size` to 100% 100%.
- Section shadow on hover
  - `[data-testid="stVerticalBlock"]:has(:is(:hover, :focus-within)) { box-shadow: 0 4px 16px rgba(0,0,0,.08); }`
- Dimming non‑active sections
  - `.block-container [data-testid="stVerticalBlock"] { opacity: 1; transition: opacity .2s ease; }`
  - `.block-container:has([data-testid="stVerticalBlock"]:is(:hover, :focus-within)) > [data-testid="stVerticalBlock"] { opacity: .55; }`
  - `.block-container [data-testid="stVerticalBlock"]:is(:hover, :focus-within) { opacity: 1; }`
- Sticky header within a section
  - Add `position: sticky; top: var(--stick-top, 0); z-index: 1; background: inherit;` to the header element.
  - Ensure the parent container doesn’t clip overflow if stickiness appears broken.

Delegated JS Fallback (minimal)
```html
<script>
if (!CSS.supports('selector(:has(*))')) {
  const setActive = (el) => {
    document.querySelectorAll('.ui-section-title[data-active]')
      .forEach(n => n.removeAttribute('data-active'));
    const block = el.closest('[data-testid="stVerticalBlock"]');
    const title = block && block.querySelector('.ui-section-title');
    if (title) title.setAttribute('data-active', 'true');
  };
  document.body.addEventListener('mouseover', (e) => setActive(e.target), { passive: true });
  document.body.addEventListener('focusin', (e) => setActive(e.target));
}
</script>
```

Limitations and Caveats
- Streamlit DOM can evolve: `data-testid` values are reasonably stable but not guaranteed. After upgrading Streamlit, sanity‑check selectors with browser devtools.
- `:has()` performance: It’s dynamic; keep selectors scoped (prefix with `.block-container` or a parent id). Avoid overly broad `:has()` across the entire document.
- Cross‑widget wrapping is not possible: If you need a single hover region spanning multiple unrelated blocks, you may need to restructure with `st.container()` or combine content in a single component.
- Iframes: `st.components.v1.html` renders in an iframe. Styles/scripts inside it don’t affect the parent document. Prefer global CSS injection via `st.markdown`; avoid “lifting” scripts out of iframes.

Verification Checklist
- One active section at a time (deepest‑only rule works).
- Keyboard navigation replicates hover behavior via `:focus-within`.
- No interference with interactive controls (charts, inputs, links) and no pointer‑event issues.
- Works at common viewports and with `prefers-reduced-motion: reduce`.

Quick Start Snippet
```python
import streamlit as st

def ensure_styles():
    st.markdown('''<style>
    .ui-section-title { font-weight: 700; background-image: linear-gradient(var(--accent,#ffd54f),var(--accent,#ffd54f)); background-repeat:no-repeat; background-position:0 0; background-size:100% 6px; transition:background-size .35s ease; }
    .ui-section-title:focus-visible { outline:2px solid var(--accent,#ffd54f); outline-offset:2px; }
    /* deepest-only activation */
    [data-testid="stVerticalBlock"] :is(:hover,:focus-within) :has(> [data-testid="stMarkdownContainer"] .ui-section-title) :not(:has([data-testid="stVerticalBlock"] :is(:hover,:focus-within) .ui-section-title)) .ui-section-title { background-size:100% 100%; }
    @media (prefers-reduced-motion: reduce) { .ui-section-title { transition:none; } }
    </style>''', unsafe_allow_html=True)

ensure_styles()
with st.container():
    st.markdown('<h2><span class="ui-section-title">Example Section</span></h2>', unsafe_allow_html=True)
    st.write('Content…')
```

