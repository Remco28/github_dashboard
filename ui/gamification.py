import streamlit as st
from typing import List, Tuple
from services.gamification import Badge, StreakStats
from models.github_types import RepoSummary


def render_badges(badges: List[Badge]) -> None:
    """
    Render badges as horizontal chips with emoji and tooltips.
    
    Args:
        badges: List of Badge objects to display
    """
    if not badges:
        st.info("🏆 Complete coding activities to earn badges!")
        return
    
    # Create columns for badges
    cols = st.columns(min(len(badges), 4))  # Max 4 badges per row
    
    for i, badge in enumerate(badges):
        with cols[i % 4]:
            # Create a metric-style display for each badge
            st.metric(
                label="",
                value=f"{badge.emoji} {badge.label}",
                help=badge.description
            )
    
    # If more than 4 badges, create a second row
    if len(badges) > 4:
        cols2 = st.columns(min(len(badges) - 4, 4))
        for i, badge in enumerate(badges[4:8]):  # Show up to 8 badges total
            with cols2[i]:
                st.metric(
                    label="",
                    value=f"{badge.emoji} {badge.label}",
                    help=badge.description
                )


def render_streaks(stats: StreakStats) -> None:
    """
    Render streak statistics with progress-style visuals.
    
    Args:
        stats: StreakStats containing current and longest streak data
    """
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Current Streak",
            f"{stats.current} days",
            help="Consecutive days with commits"
        )
    
    with col2:
        st.metric(
            "Longest Streak",
            f"{stats.longest} days",
            help="Your best consecutive streak"
        )
    
    with col3:
        if stats.last_active:
            st.metric(
                "Last Active",
                stats.last_active,
                help="Most recent day with commits"
            )
        else:
            st.metric(
                "Last Active",
                "N/A",
                help="No recent activity found"
            )
    
    # Progress visualization for current streak
    if stats.longest > 0:
        progress = min(stats.current / max(stats.longest, 7), 1.0)  # Cap at 100%
        progress_text = f"{stats.current}/{max(stats.longest, 7)} days"
        
        if stats.current > stats.longest:
            progress_text = f"🔥 New record! {stats.current} days"
        
        st.progress(
            progress,
            text=progress_text
        )
        
        # Streak status message
        if stats.current == 0:
            if stats.longest > 0:
                st.warning(f"💪 Time to start a new streak! Your best was {stats.longest} days.")
            else:
                st.info("🚀 Ready to start your coding streak journey?")
        elif stats.current >= 7:
            st.success(f"🔥 Amazing! You're on a {stats.current}-day streak!")
        elif stats.current >= 3:
            st.info(f"👍 Good momentum! {stats.current} days and counting.")
        else:
            st.info(f"🌱 Getting started! {stats.current} day streak.")
    else:
        st.info("📊 Start committing code to build your streak!")


def render_stale_nudges(items: List[Tuple[RepoSummary, int]], limit: int = 5) -> None:
    """
    Render a list of stale repositories needing attention.
    
    Args:
        items: List of tuples (RepoSummary, days_since_push)
        limit: Maximum number of repositories to show
    """
    if not items:
        st.success("✨ All your repositories are up to date!")
        return
    
    st.subheader("🚨 Repositories Needing Attention")
    
    # Show up to the limit
    displayed_items = items[:limit]
    
    for repo, days_stale in displayed_items:
        # Create columns for repo info
        col_name, col_days, col_link = st.columns([3, 1, 1])
        
        with col_name:
            # Add emoji based on staleness severity
            if days_stale > 180:
                emoji = "☠️"
                severity = "critical"
            elif days_stale > 90:
                emoji = "🚨"
                severity = "high"
            elif days_stale > 30:
                emoji = "⚠️"
                severity = "medium"
            else:
                emoji = "💤"
                severity = "low"
            
            st.write(f"{emoji} **{repo.name}**")
            
            # Show additional context
            language = f" • {repo.language}" if repo.language else ""
            private_indicator = " 🔒" if repo.private else ""
            st.caption(f"{repo.full_name}{language}{private_indicator}")
        
        with col_days:
            if days_stale == 9999:
                st.write("**Unknown**")
            else:
                st.write(f"**{days_stale}d**")
        
        with col_link:
            if repo.html_url:
                st.link_button("Open", repo.html_url, help="Open repository on GitHub")
    
    # Show count summary
    total_stale = len(items)
    if total_stale > limit:
        st.info(f"📊 Showing {limit} of {total_stale} stale repositories. Adjust your stale threshold to see fewer items.")
    else:
        st.info(f"📊 Found {total_stale} repositories that could use some attention.")
    
    # Motivational message
    if total_stale > 0:
        st.markdown(
            "💡 **Pro tip**: Even a small commit like updating documentation can bring a repository back to life! "
            "Consider archiving repositories you no longer maintain."
        )