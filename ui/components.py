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
    
    # Display metrics in columns: Total | Private | Public | Archived | Languages
    col1, col2, col3, col4, col5 = st.columns(5)
    
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
            help="Number of private repositories"
        )

    with col3:
        st.metric(
            "Public",
            public_count,
            help="Number of public repositories"
        )

    with col4:
        st.metric(
            "Archived",
            archived_count,
            help="Number of archived repositories"
        )
    
    with col5:
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
        width='stretch',
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn(
                "Name",
                help="Repository name",
                width="medium",
                max_chars=40,
            ),
            "URL": st.column_config.LinkColumn(
                "URL",
                help="Open repository on GitHub",
                width="large"
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
                width="small"
            ),
            "Language": st.column_config.TextColumn(
                "Language",
                help="Primary language",
                width="small"
            )
        },
        column_order=["Name", "Private", "Stars", "Forks", "Open Issues", "Language", "Last Push", "URL"]
    )




def render_repo_selector_with_search(options: list[str], key: str, help_text: str) -> str | None:
    """Render an enhanced repository selector with search capability for large lists."""
    if len(options) <= 20:
        # Use simple selectbox for small lists
        return st.selectbox(
            "Select repository to view tasks:",
            options=options,
            key=key,
            help=help_text
        )
    else:
        # Use search-enabled selector for large lists
        search_query = st.text_input(
            "Search repositories:",
            placeholder="Type to filter repositories...",
            key=f"{key}_search",
            help="Filter repositories by name (case-insensitive)"
        )

        if search_query.strip():
            filtered_options = [opt for opt in options if search_query.lower() in opt.lower()]
            if not filtered_options:
                st.info(f"No repositories match '{search_query}'. Showing all repositories.")
                filtered_options = options
        else:
            filtered_options = options

        return st.selectbox(
            f"Select repository to view tasks ({len(filtered_options)} shown):",
            options=filtered_options,
            key=key,
            help=help_text
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
