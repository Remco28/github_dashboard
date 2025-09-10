---
title: UI Polish and Layout Fixes
date: 2025-09-09
status: open
priority: high
assignee: DEVELOPER
---

### Objective

Based on design review feedback (ref: `@comms/ui/reference/github_dashboard_9_9_2025_001.png`), this task is to apply a round of UI polish to improve visual structure, control visibility, and fix responsive layout issues.

### 1. Improve Layout and Structure

**Goal:** Encapsulate primary content areas in distinct visual containers to improve page hierarchy and scannability.

**Affected Sections:**
- `Project Tasks`
- `Repository Progress`
- `Task List Viewer`

**Instructions:**

- **Wrap Sections in Containers:** For each of the affected sections, wrap the content in a container `div`.
- **Apply Styling:** Use custom CSS to style these containers with:
  - A light border: `1px solid #dfe1e5`
  - A subtle box-shadow: `box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.12);`
  - A border-radius: `8px`
  - Consistent internal padding: `1.5rem`
- **Implementation:** This can be achieved by creating a custom Streamlit component or by injecting CSS to style the containers that Streamlit generates for these sections.

### 2. Enhance Filter Controls

**Goal:** Improve the visibility and usability of the "Languages" multi-select dropdown in the sidebar.

**Affected Section:**
- `Filters` sidebar, specifically the "Languages" dropdown.

**Instructions:**

- **Target the Dropdown:** Apply custom CSS to the `st.multiselect` widget.
- **Styling:**
  - Give the widget a clearly defined border and background to distinguish it from the sidebar background.
  - Ensure the styling is consistent with other input elements in the sidebar for a cohesive look.
  - The placeholder text ("Choose options") should have sufficient contrast.

### 3. Refine Responsive Alignment

**Goal:** Ensure the "Repository Progress" charts align gracefully on narrower screens, avoiding awkward wrapping.

**Affected Section:**
- `Repository Progress`

**Instructions:**

- **Responsive Grid:** The Streamlit columns used for the charts should be adjusted.
- **Logic:** Instead of a fixed number of columns, the layout should be responsive. While Streamlit's native columns have limitations, we can group the charts and use CSS to create a more flexible grid.
- **Implementation:**
  - Use CSS Grid (`display: grid`) for the container holding the charts.
  - Use `grid-template-columns: repeat(auto-fill, minmax(250px, 1fr));` to allow the charts to automatically wrap and fill the available space. This will ensure the layout adapts smoothly from large screens down to mobile sizes without leaving large gaps.
