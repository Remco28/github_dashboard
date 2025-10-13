# Spec: Update NEXT_STEPS.md Logic

**Date:** 2025-10-13
**Author:** Architect
**Status:** READY
**Priority:** 1.2 (Quick Wins & Decluttering)

## 1. Objective

Update the NEXT_STEPS.md file fetching logic to support moving the file from the repository root to the `comms/` directory, with backward compatibility for repositories that still have the file at the root.

## 2. Background

Currently, the dashboard fetches `NEXT_STEPS.md` from the root of each repository (`/NEXT_STEPS.md`). To better organize project files, we want to support placing this file in `comms/NEXT_STEPS.md` instead.

This change will:
- Allow the dashboard's own `NEXT_STEPS.md` to move to `comms/`
- Support a cleaner repository structure
- Maintain compatibility with existing repositories

## 3. Scope

**In Scope:**
- Modify `services/next_steps.py` to try `comms/NEXT_STEPS.md` first
- Fall back to `/NEXT_STEPS.md` if the file is not found in `comms/`
- Handle 404 errors gracefully for both locations
- Update documentation to recommend the new location

**Out of Scope:**
- Migrating existing repositories (user responsibility)
- Supporting other file locations beyond these two
- Changing the file format or parsing logic

## 4. Technical Specification

### 4.1 Modify `fetch_next_steps()` Function

**File:** `services/next_steps.py`

**Current Implementation (line 25-50):**
```python
def fetch_next_steps(owner: str, repo: str, token: str) -> str | None:
    """
    Fetch NEXT_STEPS.md file content from a repository.

    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub token

    Returns:
        Markdown content as string if file exists, None if not found
    """
    file_data = get_file_contents(owner, repo, "NEXT_STEPS.md", token)
    if file_data is None:
        return None

    # Decode base64 content to UTF-8 string
    content_b64 = file_data.get("content", "")
    if not content_b64:
        return None

    try:
        content_bytes = base64.b64decode(content_b64)
        return content_bytes.decode("utf-8")
    except (base64.binascii.Error, UnicodeDecodeError):
        return None
```

**New Implementation:**

```python
def fetch_next_steps(owner: str, repo: str, token: str) -> str | None:
    """
    Fetch NEXT_STEPS.md file content from a repository.

    Attempts to fetch from comms/NEXT_STEPS.md first, falls back to
    root NEXT_STEPS.md for backward compatibility.

    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub token

    Returns:
        Markdown content as string if file exists, None if not found
    """
    # Try comms/NEXT_STEPS.md first (new preferred location)
    file_data = get_file_contents(owner, repo, "comms/NEXT_STEPS.md", token)

    # Fall back to root location if not found in comms/
    if file_data is None:
        file_data = get_file_contents(owner, repo, "NEXT_STEPS.md", token)

    # If still not found, return None
    if file_data is None:
        return None

    # Decode base64 content to UTF-8 string
    content_b64 = file_data.get("content", "")
    if not content_b64:
        return None

    try:
        content_bytes = base64.b64decode(content_b64)
        return content_bytes.decode("utf-8")
    except (base64.binascii.Error, UnicodeDecodeError):
        return None
```

**Key Changes:**
1. First attempt: `get_file_contents(owner, repo, "comms/NEXT_STEPS.md", token)`
2. Second attempt (fallback): `get_file_contents(owner, repo, "NEXT_STEPS.md", token)`
3. Updated docstring to document the new behavior
4. Rest of the function remains unchanged

### 4.2 Verify 404 Handling

**File:** `services/github_client.py`

Verify that `get_file_contents()` returns `None` on 404 errors. This should already be the case, but confirm during implementation.

Expected behavior:
- 404 on `comms/NEXT_STEPS.md` → returns `None`, tries fallback
- 404 on `NEXT_STEPS.md` → returns `None`, overall function returns `None`
- Any other error → surface appropriately (rate limit, auth, etc.)

### 4.3 Update Documentation

**File:** `docs/NEXT_STEPS.template.md`

Update the template to recommend the new location:

```markdown
# NEXT STEPS Template

## Recommended Location

Place this file at either:
- `comms/NEXT_STEPS.md` (recommended for better organization)
- `NEXT_STEPS.md` (root directory, still supported for backward compatibility)

The dashboard will check both locations, preferring `comms/NEXT_STEPS.md` if it exists.
```

**File:** `README.md`

Update the NEXT_STEPS section to mention both locations:

```markdown
### NEXT_STEPS.md

Each repository can include a `NEXT_STEPS.md` file to track project tasks. The dashboard will:
1. First check `comms/NEXT_STEPS.md`
2. Fall back to `NEXT_STEPS.md` in the root directory

This allows you to organize project management files in a `comms/` directory while maintaining backward compatibility.
```

## 5. Files to Modify

### Modified Files
- `services/next_steps.py` (update `fetch_next_steps()` function)
- `docs/NEXT_STEPS.template.md` (document new preferred location)
- `README.md` (update NEXT_STEPS documentation)

### Files to Verify
- `services/github_client.py` (confirm 404 handling in `get_file_contents()`)

## 6. Acceptance Criteria

1. ✅ `fetch_next_steps()` tries `comms/NEXT_STEPS.md` first
2. ✅ Falls back to root `NEXT_STEPS.md` if comms/ version not found
3. ✅ Returns `None` if neither file exists
4. ✅ Handles 404 errors gracefully without exceptions
5. ✅ Documentation updated with new preferred location
6. ✅ Manual test: Repository with file in `comms/` → file is fetched
7. ✅ Manual test: Repository with file in root only → file is fetched
8. ✅ Manual test: Repository with no file → shows guidance message
9. ✅ Manual test: Repository with file in both locations → `comms/` version is used
10. ✅ Existing tests still pass (if any)

## 7. Testing Strategy

### Manual Testing Scenarios

**Test 1: File in comms/ only**
- Repository: Create test repo with only `comms/NEXT_STEPS.md`
- Expected: Dashboard displays tasks from that file
- Verify: Check the Project Tasks section

**Test 2: File in root only**
- Repository: Use existing repo with only `/NEXT_STEPS.md`
- Expected: Dashboard displays tasks from root file
- Verify: Backward compatibility maintained

**Test 3: File in both locations**
- Repository: Create test repo with both files (different content)
- Expected: Dashboard uses `comms/NEXT_STEPS.md` (preferred location)
- Verify: Content matches comms/ version, not root version

**Test 4: No file in either location**
- Repository: Test repo with no NEXT_STEPS.md
- Expected: Dashboard shows guidance message
- Verify: No errors or exceptions

**Test 5: Current dashboard repo**
- After implementation, move `/NEXT_STEPS.md` to `/comms/NEXT_STEPS.md`
- Expected: Dashboard continues to show its own tasks
- Verify: Dogfooding the new feature

### Automated Testing (if time permits)

Add unit test to `tests/test_next_steps.py`:

```python
def test_fetch_next_steps_prefers_comms_location(mock_github_client):
    """Test that comms/NEXT_STEPS.md is checked first."""
    # Mock get_file_contents to return data for comms/ path
    # Verify fetch_next_steps returns that data
    pass

def test_fetch_next_steps_falls_back_to_root(mock_github_client):
    """Test fallback to root location when comms/ not found."""
    # Mock get_file_contents to return None for comms/, data for root
    # Verify fetch_next_steps returns root data
    pass
```

## 8. Dependencies

**Prerequisite Tasks:**
- Task 1.4 (Introduce Basic Testing) - provides testing infrastructure

**Blocks:**
- Moving the dashboard's own `NEXT_STEPS.md` to `comms/` (user task after this is deployed)

**Related:**
- This change is independent but complements the overall "Quick Wins" priority

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Breaking existing repositories | Fallback to root ensures backward compatibility |
| Confusion about which file is used | Clear documentation; comms/ takes precedence |
| GitHub API rate limit impact | No additional API calls; same total requests |
| Path handling edge cases | Test with various path formats and special characters |

## 10. Implementation Notes

**For the Developer:**

1. The change is minimal - just update the path in the first `get_file_contents()` call
2. Test thoroughly with both file locations
3. Verify that `get_file_contents()` in `github_client.py` handles 404s by returning `None` (don't catch exceptions here)
4. The `cached_fetch_next_steps()` wrapper in `services/cache.py` should work unchanged since it wraps `fetch_next_steps()`
5. After implementation, you can move the dashboard's own NEXT_STEPS.md to verify it works

**Performance Note:**
- This adds one extra API call per repository when the file is in the root (since we try comms/ first)
- However, both attempts are cached, so the impact is minimal
- Repositories using the new location (comms/) will be more efficient (one call instead of two)

## 11. Future Enhancements

- Consider adding a user preference to control the search order
- Support additional file locations (e.g., `.github/NEXT_STEPS.md`)
- Add telemetry to track which location is most commonly used
- Create a migration guide for moving files from root to comms/

## 12. Definition of Done

- Code changes implemented and tested
- All acceptance criteria met
- Documentation updated
- Manual tests passed for all scenarios
- Dashboard's own NEXT_STEPS.md successfully moved to comms/
- Code review passed
- Spec archived to `comms/tasks/archive/`
