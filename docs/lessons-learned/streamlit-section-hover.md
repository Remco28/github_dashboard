# Lesson Learned: Section-Wide Hover Effects in Streamlit

## Problem Statement

We needed to implement hover effects on section headers that would trigger when hovering over any part of the section content (header + charts/cards), not just the header itself.

## Root Cause

**Streamlit block boundaries prevent custom HTML wrappers from enclosing section content.**

- Each Streamlit widget/header renders inside its own `[data-testid="stVerticalBlock"]` container
- Using `st.markdown("<div class='gd-section-wrap'>")` cannot span subsequent widgets
- As a result, custom wrapper divs never actually contained the charts/cards
- The `:hover` pseudo-class on custom wrappers did not represent the whole section

## Failed Approaches (What NOT to Do)

### 1. Custom HTML Wrappers + JavaScript Event Listeners
**Approach:** Wrap sections in custom divs and attach JavaScript hover listeners.
**Why it failed:** Script executed before DOM content was loaded; Streamlit's re-rendering replaced nodes, making listeners ephemeral.

### 2. MutationObserver Pattern
**Approach:** Use `MutationObserver` to detect when sections were added and attach listeners.
**Why it failed:** Script was not re-executed on Streamlit page updates; observers lost context.

### 3. Iframe Context Lifting
**Approach:** Inject script via `st.components.v1.html` and "lift" it to parent document.
**Why it failed:** Script executed in parent but still targeted wrong container (custom wrapper instead of true Streamlit block).

### 4. Force Script Re-injection
**Approach:** Remove session state checks to force script injection on every update.
**Why it failed:** Streamlit's rendering cycle made this unreliable; still targeted wrong DOM anchor.

## The Working Solution

### Use Native Streamlit Containers + CSS `:has()` Selector

#### 1. Group Header and Content Using Streamlit Containers

```python
with st.container():
    render_section_header("Visualizations", level='h2', accent='blue')
    # All section content here (charts, cards, etc.)
    render_language_pie(lang_dist)
    render_commits_bar(commits_data)
    # ...
```

**Why this works:** The `st.container()` ensures the header and all section content live within the same `[data-testid="stVerticalBlock"]` element.

#### 2. CSS-First Hover Using `:has()` Pseudo-Class

```css
/* Hover on any part of the section highlights the header */
[data-testid="stVerticalBlock"]:has(.gd-section-title):hover .gd-section-title {
    background-size: 100% 100%;
}

/* Focus-within for keyboard navigation */
[data-testid="stVerticalBlock"]:has(.gd-section-title):focus-within .gd-section-title {
    background-size: 100% 100%;
}
```

**Why this works:**
- `:has()` selector checks if a Streamlit block contains a section header
- When hovering anywhere in that block, the header style activates
- No JavaScript required for the primary path
- Keyboard focus within section also activates header

#### 3. Deepest-Only Selector (Nested Sections)

To prevent nested sections from triggering parent headers:

```css
[data-testid="stVerticalBlock"]:has(> div > .stMarkdown .gd-section-title):hover .gd-section-title {
    background-size: 100% 100%;
}
```

This ensures only the deepest containing section's header responds.

## Browser Support

- **`:has()` support:** Chromium-based browsers (Chrome, Brave, Edge), Safari
- **Fallback:** A minimal delegated JavaScript fallback can be gated behind `CSS.supports('selector(:has(*))')` for older browsers

## Implementation Reference

- **Styles:** `src/ui/styles.py` in the `ensure_section_header_styles()` function
- **Usage:** `app.py` lines 264, 336, 420, 440, 513 (all major sections use `with st.container():`)

## Key Takeaways

1. **Work with Streamlit's rendering model, not against it.** Use native containers instead of trying to inject custom HTML structure.
2. **Prefer CSS-first solutions over JavaScript** when dealing with Streamlit's dynamic re-rendering.
3. **Anchor hover state to the real DOM containers** Streamlit creates, not custom wrappers.
4. **The `:has()` pseudo-class is powerful** for parent-based styling in modern CSS.

## Date Resolved

September 2025
