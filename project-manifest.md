# Project Manifest: GitHub Repository Dashboard

**Purpose:** This file serves as the entry point for AI coding agents working on this project. It provides stable pointers to critical documentation, dynamic state files, and code entrypoints.

**How to Use:**
- Consult this manifest at the start of every session to orient yourself
- Refer back when you need to locate key project assets
- Update this file if refactoring changes the location of any listed files

---

## 1. Core Identity (Stable)
*High-level architecture, goals, and participant roles. These files change infrequently.*

- **Architecture:** `docs/ARCHITECTURE.md`
- **Roadmap/Goals:** `docs/ROADMAP.md`
- **Role Definition:** `comms/roles/ARCHITECT.md`
- **Lessons Learned:** `docs/lessons-learned/` (technical reference documentation)

## 2. Dynamic State (Volatile)
*Current status, recent work, and active tasks. Check these to understand what's happening now.*

- **Activity Log:** `comms/log.md`
- **Active Tasks:** `comms/tasks/` (current specifications)
- **Completed Tasks:** `comms/tasks/archive/` (archived specifications)
- **UI Reference Screenshots:** `comms/ui/reference/` (input for UI tasks)
- **UI After Screenshots:** `comms/ui/after/` (output from implementations)

## 3. Code & Config (Entrypoints)
*Primary technical entrypoints for understanding the application.*

### Application Entry
- **Main Application:** `app.py`

### Core Services
- **GitHub API Client:** `services/github_client.py`
- **Cache Layer:** `services/cache.py`
- **Analytics:** `services/analytics.py`
- **NEXT_STEPS Parser:** `services/next_steps.py`
- **Error Handling:** `services/errors.py`

### UI Components
- **Styles & Global CSS:** `ui/styles.py`
- **Branding & Title:** `ui/branding.py`
- **Section Headers:** `ui/headers.py`
- **Charts (Plotly):** `ui/charts.py`
- **Tables:** `ui/tables.py`
- **Metrics/Cards:** `ui/metrics.py`
- **Controls & Selectors:** `ui/controls.py`
- **Checklists (NEXT_STEPS):** `ui/checklists.py`
- **Notifications & Errors:** `ui/notifications.py`

### Models & Config
- **Data Models:** `models/github_types.py`
- **Settings:** `config/settings.py`

### Configuration Files
- **Dependencies:** `requirements.txt`
- **Environment Template:** `.env` (not committed; use for local setup reference)
- **Streamlit Config:** `.streamlit/config.toml`

## 4. Development Guidelines

### Workflow
1. **Discuss & Decide:** Architect analyzes goals and recommends solutions
2. **Specify:** Architect creates task specs in `comms/tasks/`
3. **Log Status:** Updates posted to `comms/log.md`
4. **Execute:** Developer implements from spec
5. **Review & Archive:** Architect reviews and archives to `comms/tasks/archive/`

### Key Principles
- Keep services UI-agnostic; Streamlit code belongs in `app.py` and `ui/*`
- Use default Streamlit light theme for consistency
- Handle empty/edge cases with clear UI states
- Update `docs/ARCHITECTURE.md` when adding new integration points
- Update this manifest when refactoring changes file locations

## 5. Project-Specific Notes

### Process Architecture
Single-process Streamlit application:
- UI (`app.py`) → Services Layer → GitHub API
- In-memory TTL cache (no external cache required)
- No database for MVP

### Authentication
- Personal Access Token (PAT) via environment variable
- Token remains server-side; never logged or rendered

### Time Handling
- External timestamps (GitHub API) are ISO strings with `Z`
- Parse to timezone-aware UTC for safe comparisons
- Use `datetime.now(timezone.utc)` for API windows

### UI Architecture Notes
- Former `ui/components.py` decomposed into specialized modules
- Section headers use CSS `:has()` for hover effects with `st.container()` grouping
- See `docs/lessons-learned/streamlit-section-hover.md` for implementation patterns
