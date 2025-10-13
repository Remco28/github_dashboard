# Spec: Introduce Basic Testing

**Date:** 2025-10-13
**Author:** Architect
**Status:** READY
**Priority:** 1.4 (Quick Wins & Decluttering)

## 1. Objective

Establish a testing foundation with `pytest` to prevent regressions as we refactor and enhance the dashboard. This creates a safety net before making significant changes in subsequent Priority 1 tasks.

## 2. Background

The dashboard currently has no automated tests. As we prepare to remove gamification, update NEXT_STEPS logic, and add new table features, we need confidence that existing functionality remains intact.

## 3. Scope

**In Scope:**
- Create `tests/` directory structure
- Add `pytest` and `pytest-mock` to project dependencies
- Write initial unit tests for at least one service module
- Document testing approach in README

**Out of Scope:**
- Comprehensive test coverage (this is a foundation, not full coverage)
- Integration tests or end-to-end tests
- Testing Streamlit UI components (complex; defer to future work)

## 4. Technical Specification

### 4.1 Directory Structure

Create the following structure:

```
tests/
├── __init__.py
├── test_analytics.py
└── test_github_client.py (optional, if time permits)
```

### 4.2 Dependencies

Add to `requirements.txt`:
```
pytest>=7.4.0
pytest-mock>=3.11.0
```

### 4.3 Test Coverage - Analytics Module

File: `tests/test_analytics.py`

Write unit tests for functions in `services/analytics.py`. Focus on:

1. **`filter_repos()`** - Test filtering logic
   - Test language filtering
   - Test visibility filtering (public/private)
   - Test activity window filtering
   - Test search query filtering
   - Test combined filters

2. **`language_distribution()`** - Test aggregation
   - Test with repos having various languages
   - Test with empty repo list
   - Test with repos having no language data

3. **`commits_per_repo()`** - Test commit counting (with mocked API responses)
   - Test with valid commit data
   - Test with empty commit data
   - Test respecting max_repos limit

**Testing Approach:**
- Use `pytest-mock` to mock GitHub API calls in `services/github_client.py`
- Create fixture data representing `RepoSummary` objects
- Test edge cases: empty lists, None values, missing fields

### 4.4 Test Execution

Ensure tests can be run with:
```bash
pytest tests/
```

Or for verbose output:
```bash
pytest tests/ -v
```

### 4.5 Documentation

Update `README.md` with a new "Testing" section:

```markdown
## Testing

This project uses pytest for automated testing.

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-mock

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_analytics.py
```

### Writing Tests

Tests are located in the `tests/` directory. Use `pytest-mock` for mocking external dependencies like GitHub API calls.
```

## 5. Files to Modify

### New Files
- `tests/__init__.py` (empty file)
- `tests/test_analytics.py` (new tests)

### Modified Files
- `requirements.txt` (add pytest dependencies)
- `README.md` (add Testing section)

## 6. Acceptance Criteria

1. ✅ `tests/` directory exists with `__init__.py`
2. ✅ `pytest` and `pytest-mock` added to `requirements.txt`
3. ✅ `tests/test_analytics.py` exists with at least 5 test functions covering:
   - `filter_repos()` with multiple filter scenarios
   - `language_distribution()` with edge cases
   - At least one test using mocked data
4. ✅ All tests pass when running `pytest tests/`
5. ✅ README includes Testing section with clear instructions
6. ✅ Tests demonstrate both positive cases and edge cases (empty data, None values)

## 7. Testing Notes

**For the Developer:**
- Don't aim for 100% coverage; focus on establishing patterns
- Mock external dependencies (GitHub API, cache) to keep tests fast and isolated
- Use descriptive test names: `test_filter_repos_by_language_returns_matching_repos()`
- Group related tests using test classes if helpful
- Consider using `pytest.mark.parametrize` for testing multiple similar cases

**Example Test Structure:**

```python
import pytest
from models.github_types import RepoSummary
from services.analytics import filter_repos, language_distribution

@pytest.fixture
def sample_repos():
    """Fixture providing sample repository data."""
    return [
        RepoSummary(
            full_name="user/repo1",
            name="repo1",
            private=False,
            language="Python",
            # ... other required fields
        ),
        # ... more sample repos
    ]

def test_filter_repos_by_language(sample_repos):
    """Test filtering repositories by programming language."""
    result = filter_repos(sample_repos, languages={"Python"})
    assert len(result) > 0
    assert all(repo.language == "Python" for repo in result)
```

## 8. Dependencies

**Prerequisite Tasks:** None (this is the foundation)

**Blocks:** Tasks 1.1, 1.2, 1.3 should ideally run tests after implementation to verify no regressions

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Tests are brittle and break with minor changes | Focus on testing public interfaces and behavior, not implementation details |
| Mocking is complex for GitHub API | Start with simple analytics functions; defer complex API mocking to future work |
| Time investment delays other Priority 1 tasks | Keep scope minimal; 5-10 good tests are better than attempting full coverage |

## 10. Future Enhancements

After this foundation is established:
- Add tests for `services/next_steps.py` parser logic
- Add tests for `services/cache.py` TTL behavior
- Consider integration tests for GitHub API client
- Explore Streamlit testing approaches for UI components
