# NEXT STEPS – GitHub Repository Dashboard

This repository's working checklist aligned with the refocus plan (see `comms/tasks/2025-10-13-refocus-and-test.md`).

## Priority 1: Quick Wins & Decluttering

### Remove Gamification
- [x] Delete `services/gamification.py`
- [x] Remove gamification UI code from `ui/gamification.py`
- [x] Remove "Motivation" section from `app.py` (streaks & badges)
- [x] Remove "Nudges" section from `app.py` (stale repos)
- [x] Update documentation to reflect removal

### Update NEXT_STEPS.md Logic
- [x] Modify `services/next_steps.py` to check `comms/NEXT_STEPS.md` first
- [x] Add fallback to root `/NEXT_STEPS.md` for backward compatibility
- [x] Handle 404 errors gracefully when trying both locations

### Add "Last Push Date" to Main Table
- [x] Add "Last Push" column to repository table in `ui/tables.py`
- [x] Make column sortable
- [x] Display in human-readable format (e.g., "3 weeks ago")
- [x] Update table rendering in `app.py`

### Introduce Basic Testing
- [x] Create `tests/` directory
- [x] Add `pytest` to `requirements.txt`
- [x] Create `tests/test_analytics.py` with initial unit tests
- [x] Document testing approach in README

## Priority 2: Major Usability Enhancements

### Implement Sorting & Filtering
- [ ] Add text input for repository name filtering in `app.py`
- [ ] Enhance table component to support multi-column sorting
- [ ] Ensure sorting works with: Name, Last Push, Open PRs

### Add Pull Request Data
- [ ] Update `services/github_client.py` to fetch open PR data
- [ ] Add caching for PR data in `services/cache.py`
- [ ] Add "Open PRs" column to repository table
- [ ] Consider highlighting PRs awaiting user's review

## Priority 3: Future Feature Planning

### Design "What's New Since Last Visit"
- [ ] Research storage options (localStorage, session state, etc.)
- [ ] Design efficient diff algorithm for changed repos
- [ ] Design visual representation for "new" activity
- [ ] Create technical specification for implementation

## Polish & Minor Improvements

### Appearance Tweaks
- [ ] Remove lingering inline styles from Achievements badges (now obsolete after gamification removal)
- [ ] Consider extended activity windows (730 days, "All time" with rate-limit guidance)

### Documentation Updates
- [ ] Update `docs/ROADMAP.md` to reflect refocus plan
- [ ] Update `README.md` with new feature set
- [ ] Update `docs/ARCHITECTURE.md` after gamification removal
- [x] Move this file to `comms/` once app supports new location (Task 1.2)

---

**Notes:**

- This checklist is aligned with the refocus specification at `comms/tasks/2025-10-13-refocus-and-test.md`
- Priorities should be executed in order: P1 → P2 → P3
- File now lives in `comms/NEXT_STEPS.md`, matching the preferred location supported by Task 1.2
- Use `- [ ]` and `- [x]` checkboxes under headings; the parser recognizes H1–H3 section headers
