# Spec: Remove Gamification

**Date:** 2025-10-13
**Author:** Architect
**Status:** READY
**Priority:** 1.1 (Quick Wins & Decluttering)

## 1. Objective

Remove the "Motivation" (streaks & badges) and "Nudges" (stale repositories) sections from the dashboard to refocus on core value: providing a fast way to catch up on repository status.

## 2. Background

The gamification features (activity streaks, achievement badges, stale repo nudges) were experimental motivational elements. User feedback and product analysis indicate these features:
- Distract from the dashboard's core purpose
- Add visual clutter
- Are less valuable than actionable repository data

The stale repository information will be preserved in a more useful form via Task 1.3 (sortable "Last Push" column in the main table).

## 3. Scope

**In Scope:**
- Remove "Motivation" section UI (streaks, badges) from `app.py`
- Remove "Nudges" section UI (stale repos) from `app.py`
- Delete gamification service logic: `services/gamification.py`
- Remove gamification UI components: `ui/gamification.py`
- Remove all imports and references to gamification code
- Update documentation to reflect removal

**Out of Scope:**
- Replacing stale repo functionality (covered in Task 1.3)
- Removing analytics or chart functions (those remain valuable)

## 4. Technical Specification

### 4.1 Remove Sections from `app.py`

**Location:** Lines 439-509 (Motivation section) and lines 511-528 (Nudges section)

**Action:** Delete the following code blocks:

1. **Motivation Section** (approximately lines 439-509):
   ```python
   # Motivation Section (Streaks & Badges)
   st.markdown("---")
   with st.container():
       render_section_header("Motivation", level='h2', accent='purple')

       if filtered_repos:
           # ... entire motivation section ...
   ```

2. **Nudges Section** (approximately lines 511-528):
   ```python
   # Nudges Section (Stale Repositories)
   st.markdown("---")
   with st.container():
       render_section_header("Nudges", level='h2', accent='red')

       if filtered_repos:
           # ... entire nudges section ...
   ```

**Note:** Verify line numbers during implementation as they may have shifted.

### 4.2 Remove Service Module

**Action:** Delete the file:
```
services/gamification.py
```

This file contains:
- `compute_streaks()`
- `assign_badges()`
- `detect_stale_repos()`
- `compute_activity_dates()`

### 4.3 Remove UI Module

**Action:** Delete the file:
```
ui/gamification.py
```

This file contains:
- `render_streaks()`
- `render_badges()`
- `render_stale_nudges()`

### 4.4 Clean Up Imports in `app.py`

Remove the following imports from `app.py` (approximately lines 25-27):

```python
from services.gamification import assign_badges, compute_activity_dates, detect_stale_repos
from ui.gamification import render_badges, render_stale_nudges, render_streaks
```

Also remove this import (approximately line 18):
```python
cached_compute_streaks,  # from services.cache import
```

### 4.5 Clean Up Cache Functions

**File:** `services/cache.py`

**Action:** Remove the `cached_compute_streaks()` function and its `@st.cache_data` wrapper (if it exists as a separate cached function).

**Note:** If `compute_streaks()` was called directly from `services/gamification`, and the cached wrapper is in that file, this step is automatically handled by deleting `services/gamification.py`.

### 4.6 Remove Sidebar Control (if exists)

Check `app.py` sidebar section for any gamification-related controls:
- "Stale Threshold (days)" slider (approximately line 162-168)

**Action:** Remove the stale threshold slider as it's no longer used after this change.

### 4.7 Documentation Updates

Update the following documentation files:

**File:** `docs/ARCHITECTURE.md`

Remove or update references to:
- Gamification services in the "Core Services" section
- "Motivation" and "Nudges" sections in the data flow examples
- Any architecture diagrams or process descriptions mentioning gamification

**File:** `docs/ROADMAP.md`

Update:
- Phase 5 status note (already marked as "Removed")
- Add note in "Post-MVP Refinement Plan" confirming Priority 1 completion

**File:** `README.md`

Remove:
- Any screenshots showing Motivation or Nudges sections
- Feature descriptions mentioning streaks, badges, or nudges
- Update feature list to reflect current sections only

## 5. Files to Modify

### Files to Delete
- `services/gamification.py`
- `ui/gamification.py`

### Files to Modify
- `app.py` (remove sections, imports, sidebar controls)
- `services/cache.py` (remove cached_compute_streaks if separate)
- `docs/ARCHITECTURE.md` (update service descriptions)
- `docs/ROADMAP.md` (note completion)
- `README.md` (update features, screenshots)

## 6. Acceptance Criteria

1. ✅ `services/gamification.py` deleted
2. ✅ `ui/gamification.py` deleted
3. ✅ "Motivation" section removed from `app.py`
4. ✅ "Nudges" section removed from `app.py`
5. ✅ All gamification imports removed from `app.py`
6. ✅ Stale threshold slider removed from sidebar (if present)
7. ✅ `cached_compute_streaks` removed from `services/cache.py` imports
8. ✅ App runs without errors: `streamlit run app.py`
9. ✅ No references to gamification remain in codebase (verify with grep)
10. ✅ Documentation updated (ARCHITECTURE, ROADMAP, README)
11. ✅ Remaining sections render correctly: Visualizations, Project Tasks, Task List Viewer

## 7. Testing Notes

**Manual Testing:**
1. Run `streamlit run app.py`
2. Verify no Python import errors
3. Verify the following sections display correctly:
   - Summary Statistics (cards)
   - Repository Table
   - Visualizations (charts)
   - Project Tasks (NEXT_STEPS aggregate)
   - Task List Viewer (per-repo NEXT_STEPS)
4. Verify no visual artifacts or broken layouts where sections were removed
5. Test filters and controls to ensure no regressions

**Code Verification:**
```bash
# Verify no lingering references to gamification
grep -r "gamification" --include="*.py" .
grep -r "streaks" --include="*.py" . | grep -v "# streaks"
grep -r "badges" --include="*.py" . | grep -v "# badges"
grep -r "stale_repos" --include="*.py" .
grep -r "nudges" --include="*.py" . | grep -v "# nudges"
```

All searches should return zero results (or only comments/documentation).

**Automated Testing:**
After implementation, run existing tests:
```bash
pytest tests/ -v
```

## 8. Dependencies

**Prerequisite Tasks:**
- Task 1.4 (Introduce Basic Testing) - recommended to complete first for safety net

**Blocks:** None, but Task 1.3 provides the replacement for stale repo information

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Accidental removal of shared utility functions | Carefully audit imports; grep for function usage before deleting |
| Breaking changes to data flow | Test all remaining sections after removal |
| Cached data references to removed functions | Clear Streamlit cache after deployment |
| Documentation drift | Systematically update all docs mentioning gamification |

## 10. Rollback Plan

If issues arise:
1. Restore deleted files from git: `git checkout HEAD -- services/gamification.py ui/gamification.py`
2. Restore removed sections in `app.py` from git history
3. Re-add imports

## 11. Future Considerations

- The stale repository detection logic may be useful for Task 1.3 (Last Push column)
- Consider extracting the date-formatting utilities if they were in `services/gamification.py` and are needed elsewhere
- Activity date computation logic may be valuable for future "What's New" feature (Priority 3)

## 12. Definition of Done

- All code deletions complete
- App runs without errors
- All remaining sections functional
- Documentation reflects current feature set
- No gamification references in codebase (verified via grep)
- Code review passed
- Spec archived to `comms/tasks/archive/`
