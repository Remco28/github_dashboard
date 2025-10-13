# Spec: Add Last Push Date to Main Table

**Date:** 2025-10-13
**Author:** Architect
**Status:** READY
**Priority:** 1.3 (Quick Wins & Decluttering)

## 1. Objective

Enhance the main repository table by making the "Last Push" column more prominent and useful with human-readable relative dates (e.g., "3 weeks ago"), replacing the functionality of the removed "Nudges" section.

## 2. Background

The "Nudges" section (removed in Task 1.1) displayed stale repositories separately. This was visually distracting and required users to look in multiple places for repository status.

By enhancing the "Last Push" column in the main table, we:
- Keep stale repository information visible and actionable
- Reduce visual clutter by consolidating information
- Make the table more useful as a primary dashboard view
- Maintain all sorting capabilities

## 3. Scope

**In Scope:**
- Convert "Last Push" column to human-readable relative format (e.g., "3 weeks ago", "2 days ago")
- Ensure column remains sortable by actual date/time
- Maintain existing column order and configuration
- Add visual indicators for very stale repositories (optional enhancement)

**Out of Scope:**
- Adding new table columns (focus on improving existing Last Push column)
- Changing table layout or other columns
- Re-implementing the "Nudges" section (it's being removed)

## 4. Technical Specification

### 4.1 Current Implementation Analysis

**File:** `ui/tables.py` (lines 18-26, 52)

Current code displays date in ISO format (YYYY-MM-DD):
```python
pushed_date = "N/A"
if repo.pushed_at:
    try:
        date_str = repo.pushed_at.replace('Z', '+00:00') if repo.pushed_at.endswith('Z') else repo.pushed_at
        from datetime import datetime
        dt = datetime.fromisoformat(date_str.split('T')[0])
        pushed_date = dt.strftime('%Y-%m-%d')
    except (ValueError, AttributeError):
        pushed_date = repo.pushed_at[:10] if len(repo.pushed_at) >= 10 else repo.pushed_at
```

### 4.2 New Implementation - Relative Date Format

**File:** `ui/tables.py`

Create a helper function to format relative dates:

```python
from datetime import datetime, timezone

def format_relative_date(iso_timestamp: str | None) -> str:
    """
    Format an ISO timestamp as a human-readable relative date.

    Args:
        iso_timestamp: ISO 8601 timestamp string (e.g., "2025-09-15T10:30:00Z")

    Returns:
        Human-readable relative date (e.g., "3 weeks ago", "2 days ago", "N/A")
    """
    if not iso_timestamp:
        return "N/A"

    try:
        # Parse ISO timestamp to timezone-aware datetime
        date_str = iso_timestamp.replace('Z', '+00:00') if iso_timestamp.endswith('Z') else iso_timestamp
        dt = datetime.fromisoformat(date_str)

        # Ensure timezone-aware comparison
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        # Calculate time difference
        now = datetime.now(timezone.utc)
        delta = now - dt

        # Format as relative time
        days = delta.days
        hours = delta.seconds // 3600

        if days == 0:
            if hours == 0:
                return "Just now"
            elif hours == 1:
                return "1 hour ago"
            else:
                return f"{hours} hours ago"
        elif days == 1:
            return "Yesterday"
        elif days < 7:
            return f"{days} days ago"
        elif days < 30:
            weeks = days // 7
            return f"{weeks} week{'s' if weeks > 1 else ''} ago"
        elif days < 365:
            months = days // 30
            return f"{months} month{'s' if months > 1 else ''} ago"
        else:
            years = days // 365
            return f"{years} year{'s' if years > 1 else ''} ago"

    except (ValueError, AttributeError, TypeError):
        return "Unknown"
```

**Update the table rendering code:**

```python
def render_repo_table(repo_summaries: list[RepoSummary]) -> None:
    """Display a sortable table of repositories."""
    if not repo_summaries:
        st.warning("No repositories match the current filters.")
        st.info("💡 Try adjusting your filters or click 'Clear All Filters' to reset.")
        return

    st.subheader(f"Repository Details ({len(repo_summaries)} repositories)")

    df_data = []
    for repo in repo_summaries:
        # Format last push date as relative time
        pushed_date = format_relative_date(repo.pushed_at)

        df_data.append({
            "Name": repo.name,
            "Private": "🔒" if repo.private else "🔓",
            "Stars": repo.stargazers_count,
            "Forks": repo.forks_count,
            "Open Issues": repo.open_issues_count,
            "Language": repo.language or "N/A",
            "Last Push": pushed_date,
            "URL": repo.html_url,
        })

    df = pd.DataFrame(df_data)

    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", help="Repository name", width="medium"),
            "URL": st.column_config.LinkColumn("URL", help="Open repository on GitHub", width="large"),
            "Stars": st.column_config.NumberColumn("Stars", help="Number of stars", width="small"),
            "Forks": st.column_config.NumberColumn("Forks", help="Number of forks", width="small"),
            "Open Issues": st.column_config.NumberColumn("Open Issues", help="Number of open issues", width="small"),
            "Private": st.column_config.TextColumn("Visibility", help="Repository visibility", width="small"),
            "Last Push": st.column_config.TextColumn("Last Push", help="Time since last push (click to sort)", width="medium"),
            "Language": st.column_config.TextColumn("Language", help="Primary language", width="small"),
        },
        column_order=["Name", "Private", "Stars", "Forks", "Open Issues", "Language", "Last Push", "URL"],
    )
```

### 4.3 Sorting Considerations

**Important:** Streamlit's `st.dataframe` with string columns sorts alphabetically, which won't work correctly for relative dates.

**Solution 1 (Recommended):** Add a hidden sortable column with numeric days value:

```python
df_data.append({
    "Name": repo.name,
    "Private": "🔒" if repo.private else "🔓",
    "Stars": repo.stargazers_count,
    "Forks": repo.forks_count,
    "Open Issues": repo.open_issues_count,
    "Language": repo.language or "N/A",
    "Last Push": format_relative_date(repo.pushed_at),
    "_days_since_push": calculate_days_since(repo.pushed_at),  # Hidden numeric column
    "URL": repo.html_url,
})
```

Then configure the dataframe to hide the numeric column but allow sorting:

```python
column_config={
    # ... other columns ...
    "Last Push": st.column_config.TextColumn("Last Push", help="Time since last push (click to sort)", width="medium"),
    "_days_since_push": None,  # Hide the column but keep it for sorting
}
```

**Helper function:**

```python
def calculate_days_since(iso_timestamp: str | None) -> int:
    """
    Calculate days since the given ISO timestamp.

    Returns a large number (9999) for N/A timestamps to sort them last.
    """
    if not iso_timestamp:
        return 9999

    try:
        date_str = iso_timestamp.replace('Z', '+00:00') if iso_timestamp.endswith('Z') else iso_timestamp
        dt = datetime.fromisoformat(date_str)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)

        now = datetime.now(timezone.utc)
        delta = now - dt
        return delta.days
    except (ValueError, AttributeError, TypeError):
        return 9999
```

### 4.4 Optional Enhancement: Visual Indicators

Consider adding visual indicators for very stale repositories:

```python
def format_relative_date(iso_timestamp: str | None, add_indicator: bool = True) -> str:
    """Format with optional staleness indicator."""
    relative_date = # ... existing logic ...

    if add_indicator:
        days = calculate_days_since(iso_timestamp)
        if days > 180:  # 6 months
            return f"⚠️ {relative_date}"
        elif days > 90:  # 3 months
            return f"⏰ {relative_date}"

    return relative_date
```

**Note:** This is optional. Discuss with product owner before implementing.

## 5. Files to Modify

### Modified Files
- `ui/tables.py` (add helper functions, update table rendering)

### No Changes Required
- `app.py` (table rendering call remains the same)
- `models/github_types.py` (RepoSummary unchanged)

## 6. Acceptance Criteria

1. ✅ "Last Push" column displays relative dates (e.g., "3 weeks ago", "2 days ago")
2. ✅ Column is sortable by actual time (not alphabetically)
3. ✅ "N/A" or "Unknown" displayed for repositories with no push date
4. ✅ Table remains responsive and maintains existing column layout
5. ✅ Relative date formatting handles edge cases:
   - Same day: "Just now" or "X hours ago"
   - Yesterday: "Yesterday"
   - Recent: "X days ago"
   - Older: "X weeks/months/years ago"
6. ✅ Sorting works correctly (most recent first, oldest last)
7. ✅ No performance regression (formatting is fast)
8. ✅ All existing tests pass
9. ✅ Manual test with repositories of varying ages confirms correct display

## 7. Testing Strategy

### Manual Testing

**Test with various repository ages:**
1. Repository pushed today → "Just now" or "X hours ago"
2. Repository pushed yesterday → "Yesterday"
3. Repository pushed 5 days ago → "5 days ago"
4. Repository pushed 3 weeks ago → "3 weeks ago"
5. Repository pushed 6 months ago → "6 months ago"
6. Repository pushed 2 years ago → "2 years ago"
7. Repository with no push date → "N/A"

**Test sorting:**
1. Click "Last Push" column header
2. Verify repositories sort by actual age (not alphabetically)
3. Most recent should appear first (or last, depending on sort direction)

**Test edge cases:**
1. Repository pushed in the last hour
2. Repository pushed exactly 7 days ago (boundary)
3. Repository pushed exactly 30 days ago (boundary)
4. Repository with malformed timestamp

### Automated Testing

Add to `tests/test_tables.py` (new file):

```python
from ui.tables import format_relative_date, calculate_days_since
from datetime import datetime, timezone, timedelta

def test_format_relative_date_just_now():
    now = datetime.now(timezone.utc)
    timestamp = now.isoformat()
    assert format_relative_date(timestamp) in ["Just now", "1 hour ago"]

def test_format_relative_date_days_ago():
    five_days_ago = datetime.now(timezone.utc) - timedelta(days=5)
    timestamp = five_days_ago.isoformat()
    assert format_relative_date(timestamp) == "5 days ago"

def test_format_relative_date_weeks_ago():
    three_weeks_ago = datetime.now(timezone.utc) - timedelta(weeks=3)
    timestamp = three_weeks_ago.isoformat()
    assert format_relative_date(timestamp) == "3 weeks ago"

def test_format_relative_date_none():
    assert format_relative_date(None) == "N/A"

def test_calculate_days_since():
    five_days_ago = datetime.now(timezone.utc) - timedelta(days=5)
    timestamp = five_days_ago.isoformat()
    assert calculate_days_since(timestamp) == 5
```

## 8. Dependencies

**Prerequisite Tasks:**
- Task 1.4 (Introduce Basic Testing) - provides test infrastructure
- Task 1.1 (Remove Gamification) - removes the "Nudges" section this replaces

**Blocks:** None

**Related:**
- This completes the "Quick Wins" priority by making stale repository information more accessible

## 9. Risks & Mitigations

| Risk | Mitigation |
|------|-----------|
| Sorting doesn't work correctly with text dates | Use hidden numeric column for sorting |
| Relative dates confusing for users | Keep format simple and intuitive; add tooltip |
| Performance issues with date calculations | Format calculation is O(n) and fast; acceptable for typical repo counts |
| Timezone handling edge cases | Use timezone-aware UTC throughout; test boundaries |
| Users prefer absolute dates | Can add toggle in future; relative dates are standard in modern UIs |

## 10. Implementation Notes

**For the Developer:**

1. Add both helper functions at the top of `ui/tables.py`
2. Keep the existing date parsing logic as fallback
3. Test with your own repositories to verify formatting
4. Consider adding a tooltip to the column header explaining the format
5. The hidden numeric column trick is standard Streamlit practice for sortable formatted columns
6. Verify `use_container_width=True` (replaces deprecated `width='stretch'`)

**Performance Considerations:**
- Date formatting is O(n) where n = number of repos
- For typical dashboards (< 200 repos), this is negligible
- All calculations are in-memory with no API calls

**Accessibility:**
- Relative dates are more scannable than ISO dates
- Sorting by actual time preserves information
- Consider color-coding in future if staleness indicators are desired

## 11. Future Enhancements

After this task:
- Add configurable staleness threshold (user preference)
- Add visual indicators (emoji or color) for very stale repositories
- Add tooltip showing exact timestamp on hover
- Add "days since last commit" vs "days since last push" option
- Export table with both relative and absolute dates

## 12. Definition of Done

- Helper functions implemented and tested
- Table displays relative dates correctly
- Sorting works correctly (verified manually)
- Edge cases handled (N/A, just now, boundaries)
- Unit tests added and passing
- Manual testing completed with various repository ages
- No visual regressions in table layout
- Code review passed
- Spec archived to `comms/tasks/archive/`
