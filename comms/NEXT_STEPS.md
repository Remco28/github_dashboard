# NEXT STEPS – GitHub Repository Dashboard

This repository's working checklist aligned with the refocus plan (see `comms/tasks/2025-10-13-refocus-and-test.md`).

## Priority 1: Quick Wins & Decluttering

### Remove Gamification
- [ ] Delete `services/gamification.py`
- [ ] Remove gamification UI code from `ui/gamification.py`
- [ ] Remove "Motivation" section from `app.py` (streaks & badges)
- [ ] Remove "Nudges" section from `app.py` (stale repos)
- [ ] Update documentation to reflect removal

### Update NEXT_STEPS.md Logic
- [ ] Modify `services/next_steps.py` to check `comms/NEXT_STEPS.md` first
- [ ] Add fallback to root `/NEXT_STEPS.md` for backward compatibility
- [ ] Handle 404 errors gracefully when trying both locations

### Add "Last Push Date" to Main Table
- [ ] Add "Last Push" column to repository table in `ui/tables.py`
- [ ] Make column sortable
- [ ] Display in human-readable format (e.g., "3 weeks ago")
- [ ] Update table rendering in `app.py`

### Introduce Basic Testing
- [ ] Create `tests/` directory
- [ ] Add `pytest` to `requirements.txt`
- [ ] Create `tests/test_analytics.py` with initial unit tests
- [ ] Document testing approach in README

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
- [ ] Move this file to `comms/` once app supports new location (Task 1.2)

---

**Notes:**

- This checklist is aligned with the refocus specification at `comms/tasks/2025-10-13-refocus-and-test.md`
- Priorities should be executed in order: P1 → P2 → P3
- Keep the file in the repository root until Task 1.2 (NEXT_STEPS.md logic update) is completed
- Use `- [ ]` and `- [x]` checkboxes under headings; the parser recognizes H1–H3 section headers
