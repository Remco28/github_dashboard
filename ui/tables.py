from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional

import pandas as pd
import streamlit as st

from models.github_types import RepoSummary


def _parse_iso_datetime(iso_timestamp: Optional[str]) -> Optional[datetime]:
    """Convert an ISO timestamp (optionally ending with Z) into a timezone-aware UTC datetime."""
    if not iso_timestamp:
        return None

    normalized = iso_timestamp.strip()
    try:
        if "T" not in normalized:
            # Accept date-only formats by assuming start of day UTC
            normalized = f"{normalized}T00:00:00"

        if normalized.endswith("Z"):
            normalized = normalized.removesuffix("Z") + "+00:00"

        dt = datetime.fromisoformat(normalized)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        else:
            dt = dt.astimezone(timezone.utc)
        return dt
    except (ValueError, AttributeError):
        return None


def calculate_days_since(iso_timestamp: Optional[str]) -> Optional[int]:
    """Return whole days since the provided timestamp, or None when unavailable."""
    dt = _parse_iso_datetime(iso_timestamp)
    if dt is None:
        return None

    now = datetime.now(timezone.utc)
    delta = now - dt
    # Guard against future timestamps returning negative values
    if delta.days < 0:
        return 0
    return delta.days


def format_relative_date(value: Optional[datetime | str]) -> str:
    """Format a datetime (or ISO string) into a human-readable relative expression."""
    if value is None:
        return "N/A"

    # Handle pandas NaT / numpy nan
    if hasattr(pd, "isna") and pd.isna(value):  # type: ignore[arg-type]
        return "N/A"

    if isinstance(value, str):
        dt = _parse_iso_datetime(value)
    else:
        dt = value

    if dt is None:
        return "Unknown"

    now = datetime.now(timezone.utc)
    delta = now - dt

    # Future timestamps
    if delta.total_seconds() < 0:
        return "In the future"

    days = delta.days
    hours = delta.seconds // 3600
    minutes = (delta.seconds % 3600) // 60

    if days == 0:
        if hours == 0:
            if minutes <= 1:
                label = "Just now"
            else:
                label = f"{minutes} minutes ago"
        elif hours == 1:
            label = "1 hour ago"
        else:
            label = f"{hours} hours ago"
    elif days == 1:
        label = "Yesterday"
    elif days < 7:
        label = f"{days} days ago"
    elif days < 30:
        weeks = days // 7
        label = f"{weeks} week{'s' if weeks > 1 else ''} ago"
    elif days < 365:
        months = max(days // 30, 1)
        label = f"{months} month{'s' if months > 1 else ''} ago"
    else:
        years = max(days // 365, 1)
        label = f"{years} year{'s' if years > 1 else ''} ago"

    if days >= 180:
        label += " ⚠️"

    return label


def render_repo_table(repo_summaries: list[RepoSummary]) -> None:
    """Display a sortable table of repositories."""
    if not repo_summaries:
        st.warning("No repositories match the current filters.")
        st.info("💡 Try adjusting your filters or click 'Clear All Filters' to reset.")
        return

    st.subheader(f"Repository Details ({len(repo_summaries)} repositories)")

    df_data = []
    for repo in repo_summaries:
        last_push_dt = _parse_iso_datetime(repo.pushed_at)

        df_data.append(
            {
                "Name": repo.name,
                "Private": "🔒" if repo.private else "🔓",
                "Stars": repo.stargazers_count,
                "Forks": repo.forks_count,
                "Open Issues": repo.open_issues_count,
                "Language": repo.language or "N/A",
                "Last Push": last_push_dt if last_push_dt is not None else pd.NaT,
                "URL": repo.html_url,
            }
        )

    df = pd.DataFrame(df_data)
    df_styled = df.style.format({"Last Push": format_relative_date})

    st.dataframe(
        df_styled,
        width="stretch",
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", help="Repository name", width="medium", max_chars=40),
            "URL": st.column_config.LinkColumn("URL", help="Open repository on GitHub", width="large"),
            "Stars": st.column_config.NumberColumn("Stars", help="Number of stars", width="small"),
            "Forks": st.column_config.NumberColumn("Forks", help="Number of forks", width="small"),
            "Open Issues": st.column_config.NumberColumn("Open Issues", help="Number of open issues", width="small"),
            "Private": st.column_config.TextColumn("Visibility", help="Repository visibility", width="small"),
            "Last Push": st.column_config.Column(
                "Last Push",
                help="Relative time since the last push (⚠️ marks very stale repositories)",
                width="small",
            ),
            "Language": st.column_config.TextColumn("Language", help="Primary language", width="small"),
        },
        column_order=["Name", "Private", "Stars", "Forks", "Open Issues", "Language", "Last Push", "URL"],
    )
