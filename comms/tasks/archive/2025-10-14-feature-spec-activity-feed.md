# Feature Spec: "Recent Activity" Feed

**Date:** 2025-10-14
**Author:** TECHADVISOR
**Status:** READY

## 1. Overview

This document specifies the design and implementation for the **"Recent Activity"** feature, as discussed and approved. The goal is to provide users with a fast, minimal-effort way to see the latest notable events across all of their repositories.

The feature will be a new UI section that displays a chronological, log-style feed of recent, notable events from all of the user's repositories.

## 2. UI/UX Specification

### 2.1. Placement

The "Recent Activity" section will be rendered in the main application view, directly **above** the "NEXT STEPS" section.

### 2.2. Style & Format

The UI will be minimalist and styled to resemble a "console log." Each event will be represented as a single, clean line of text.

The precise format for each line is:
`[Date/Time][Repo Name][Event Type]"Event Message"`

- Date/time should reflect the event’s `created_at` in UTC (formatted as `YYYY-MM-DD HH:MM`).

**Example:**
```
[2025-10-14 10:30][github_dashboard][Commit] "Refactor data fetching logic"
[2025-10-14 09:15][my-other-project][Merge] "feat: Add new login component (#42)"
[2025-10-13 18:00][github_dashboard][Release] "v1.2.0 - Stability Improvements"
```

### 2.3. Interactivity

- The `[Repo Name]` tag will be a hyperlink to the repository's main page on GitHub.
- The `[Event Type]` tag will be a hyperlink to the most relevant GitHub resource for that event (e.g., latest commit in the push, merged PR, release page).

### 2.4. Content

- The UI will be intentionally minimal. It will **not** include author avatars, full URLs, or other metadata to avoid clutter.
- The feed will display up to **20** of the most recent events returned from the first page of the GitHub events API and will be contained in a scrollable, console-like window.
- A thin horizontal rule will separate the section header from the feed container.
- Use a popular monospace console font stack (e.g., Fira Code / JetBrains Mono fallbacks) and suppress link underlines to keep the log aesthetic clean.

## 3. Technical Implementation

### 3.1. State Management

- No persistent browser state is required for this feature. Each application load will fetch the most recent GitHub activity and render it directly.

### 3.2. Data Fetching

- A new function will be added to `services/github_client.py`.
- This function will use the **`GET /users/{username}/events`** GitHub API endpoint. This is a standard, free API call that uses the existing authentication token. No further setup is required.
- The function will fetch the first page of results only and return the events sorted in descending order by `created_at`.

### 3.3. Event Processing & Rendering

- A new module, **`ui/activity_feed.py`**, will be created to contain the rendering logic.
- This module will receive the list of event objects from the GitHub client and trim the list to the first **20** entries (if more are returned).
- It will contain logic to parse different event types and format them into the specified "console log" string format. The feature will support:
    - `PushEvent` → `[Commit]` using the latest commit in the push (link to the commit; message is the commit message).
    - `PullRequestEvent` (only when `action == "closed"` and `pull_request.merged == true`) → `[Merge]` (link to the merged PR; message is the PR title).
    - `ReleaseEvent` → `[Release]` (link to the release page; message is the release name or tag).
    - `CreateEvent` (branch only) → `[Branch]` (link to the new branch; message includes the branch name).
    - `DeleteEvent` (branch only) → `[Delete]` with the branch name (link to the repository’s main page).
    - `WatchEvent` → `[Star]` (link to the repository’s stargazers page).
    - `MemberEvent` → `[Member]` (link to the repository’s main page; message describes the collaborator added or removed).
- Any unsupported event types will be ignored to keep the feed focused and noise-free.
- The module will generate the final clickable `st.markdown` elements for display within a scrollable container.
- For repositories owned by the authenticated user, the owner prefix will be omitted from the rendered label (e.g., show `my-repo` instead of `username/my-repo`).
- The visual treatment will mimic a code editor/light-console theme: timestamps, repo names, event types, and descriptions each get distinct text colors while remaining simple inline links (no pills or background treatments).

## 4. Summary of File Changes

- **`app.py`**: Will be modified to import and call the new `ui.activity_feed` module, placing it correctly in the main layout.
- **`services/github_client.py`**: Will be updated with a new function to fetch user events.
- **`ui/activity_feed.py`**: This **new file** will be created to house the UI rendering logic for the activity feed.
