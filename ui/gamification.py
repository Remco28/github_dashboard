import streamlit as st
from typing import List, Tuple
from services.gamification import Badge, StreakStats
from models.github_types import RepoSummary


def ensure_badge_styles() -> None:
    """Inject badge card styles only once per session."""
    if st.session_state.get('_gd_badge_css_loaded'):
        return
        
    st.markdown("""
    <style>
      .gd-badges { 
        display: grid; 
        grid-template-columns: repeat(auto-fill, minmax(120px, 1fr)); 
        gap: 12px; 
        margin: 12px 0;
      }
      .gd-badge { 
        display: flex; 
        flex-direction: column; 
        align-items: center; 
        justify-content: center; 
        padding: 10px 12px; 
        border: 1px solid rgba(0,0,0,0.08); 
        border-radius: 10px; 
        background: linear-gradient(180deg, #fff, #fafafa); 
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        aspect-ratio: 1;
        min-height: 120px;
      }
      .gd-badge-emoji { 
        font-size: 28px; 
        line-height: 1; 
        margin-bottom: 6px; 
      }
      .gd-badge-label { 
        font-weight: 600; 
        text-align: center; 
        font-size: 13px; 
      }
    </style>
    """, unsafe_allow_html=True)
    st.session_state['_gd_badge_css_loaded'] = True


def render_badges(badges: List[Badge]) -> None:
    """
    Render badges as styled cards with emoji and tooltips.
    
    Args:
        badges: List of Badge objects to display
    """
    if not badges:
        st.info("🏆 Complete coding activities to earn badges!")
        return
    
    ensure_badge_styles()
    
    # Build HTML for badge grid
    badge_html = '<div class="gd-badges">'
    
    for badge in badges:
        # Escape HTML in text fields for security
        safe_label = badge.label.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        safe_desc = badge.description.replace('<', '&lt;').replace('>', '&gt;').replace('"', '&quot;')
        
        badge_html += f'''
        <div class="gd-badge" title="{safe_desc}">
            <div class="gd-badge-emoji">{badge.emoji}</div>
            <div class="gd-badge-label">{safe_label}</div>
        </div>
        '''
    
    badge_html += '</div>'
    
    st.markdown(badge_html, unsafe_allow_html=True)


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

    # Streak status message (left-aligned, below the metrics)
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
                # Compatibility: link_button was added in newer Streamlit versions
                try:
                    if hasattr(st, "link_button"):
                        st.link_button("Open", repo.html_url, help="Open repository on GitHub")
                    else:
                        st.markdown(f"[Open]({repo.html_url})")
                except Exception:
                    st.markdown(f"[Open]({repo.html_url})")
    
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
