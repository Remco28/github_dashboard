import streamlit as st
import pandas as pd
from models.github_types import RepoSummary


def render_stat_cards(repo_summaries: list[RepoSummary]) -> None:
    """Render metrics cards showing repository statistics."""
    if not repo_summaries:
        st.info("No repositories to display.")
        return
    
    # Calculate statistics
    total_repos = len(repo_summaries)
    private_count = sum(1 for repo in repo_summaries if repo.private)
    public_count = total_repos - private_count
    archived_count = sum(1 for repo in repo_summaries if repo.archived)
    languages_count = len(set(repo.language for repo in repo_summaries if repo.language))
    
    # Display metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Repositories",
            total_repos,
            help="Total number of repositories"
        )
    
    with col2:
        st.metric(
            "Private",
            private_count,
            delta=f"{public_count} public",
            help="Private vs public repositories"
        )
    
    with col3:
        st.metric(
            "Archived",
            archived_count,
            help="Number of archived repositories"
        )
    
    with col4:
        st.metric(
            "Languages",
            languages_count,
            help="Number of different programming languages"
        )


def render_repo_table(repo_summaries: list[RepoSummary]) -> None:
    """Display a sortable table of repositories."""
    if not repo_summaries:
        st.warning("No repositories match the current filters.")
        st.info("💡 Try adjusting your filters or click 'Clear All Filters' to reset.")
        return
    
    st.subheader(f"Repository Details ({len(repo_summaries)} repositories)")
    
    # Convert to DataFrame for display
    df_data = []
    for repo in repo_summaries:
        # Format date for display (just the date part)
        pushed_date = "N/A"
        if repo.pushed_at:
            try:
                # Handle ISO format with Z
                date_str = repo.pushed_at.replace('Z', '+00:00') if repo.pushed_at.endswith('Z') else repo.pushed_at
                from datetime import datetime
                dt = datetime.fromisoformat(date_str.split('T')[0])  # Just take date part
                pushed_date = dt.strftime('%Y-%m-%d')
            except (ValueError, AttributeError):
                pushed_date = repo.pushed_at[:10] if len(repo.pushed_at) >= 10 else repo.pushed_at
        
        df_data.append({
            "Name": repo.name,
            "Private": "🔒" if repo.private else "🔓",
            "Stars": repo.stargazers_count,
            "Forks": repo.forks_count,
            "Open Issues": repo.open_issues_count,
            "Language": repo.language or "N/A",
            "Last Push": pushed_date,
            "URL": repo.html_url
        })
    
    df = pd.DataFrame(df_data)
    
    # Display interactive dataframe
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config={
            "URL": st.column_config.LinkColumn(
                "Repository URL",
                help="Click to open repository on GitHub",
                width="small"
            ),
            "Stars": st.column_config.NumberColumn(
                "Stars",
                help="Number of stars",
                width="small"
            ),
            "Forks": st.column_config.NumberColumn(
                "Forks",
                help="Number of forks",
                width="small"
            ),
            "Open Issues": st.column_config.NumberColumn(
                "Open Issues",
                help="Number of open issues",
                width="small"
            ),
            "Private": st.column_config.TextColumn(
                "Visibility",
                help="Repository visibility",
                width="small"
            ),
            "Last Push": st.column_config.TextColumn(
                "Last Push",
                help="Date of last push",
                width="medium"
            )
        },
        column_order=["Name", "Private", "Stars", "Forks", "Open Issues", "Language", "Last Push", "URL"]
    )




def render_settings_help(username: str) -> None:
    """Render settings help panel in sidebar."""
    with st.sidebar.expander("Settings Help"):
        st.write(f"GitHub Username: **{username or 'Not set'}**")
        st.write("Token: loaded from environment (not displayed)")
        
        st.markdown("**Setup Steps:**")
        st.markdown("""
        • Create `.env` file with `GITHUB_TOKEN` and `GITHUB_USERNAME`
        • Token needs `repo` scope for private repos, `public_repo` for public only
        • Check `.env.example` for format reference
        • Rate limits: 5000/hour authenticated, 60/hour unauthenticated
        • Use cache controls if hitting rate limits frequently
        """)
        
        st.markdown("**Common Issues:**")
        st.markdown("""
        • **Empty repositories:** Check username spelling and token permissions
        • **Authentication errors:** Verify token is valid and has required scopes
        • **Rate limits:** Use "Bypass Cache" sparingly, or wait for reset
        • **Missing data:** Try refreshing or clearing cache
        """)
