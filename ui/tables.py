import pandas as pd
import streamlit as st

from models.github_types import RepoSummary


def render_repo_table(repo_summaries: list[RepoSummary]) -> None:
    """Display a sortable table of repositories."""
    if not repo_summaries:
        st.warning("No repositories match the current filters.")
        st.info("💡 Try adjusting your filters or click 'Clear All Filters' to reset.")
        return

    st.subheader(f"Repository Details ({len(repo_summaries)} repositories)")

    df_data = []
    for repo in repo_summaries:
        pushed_date = "N/A"
        if repo.pushed_at:
            try:
                date_str = repo.pushed_at.replace('Z', '+00:00') if repo.pushed_at.endswith('Z') else repo.pushed_at
                from datetime import datetime
                dt = datetime.fromisoformat(date_str.split('T')[0])
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
            "URL": repo.html_url,
        })

    df = pd.DataFrame(df_data)

    st.dataframe(
        df,
        width='stretch',
        hide_index=True,
        column_config={
            "Name": st.column_config.TextColumn("Name", help="Repository name", width="medium", max_chars=40),
            "URL": st.column_config.LinkColumn("URL", help="Open repository on GitHub", width="large"),
            "Stars": st.column_config.NumberColumn("Stars", help="Number of stars", width="small"),
            "Forks": st.column_config.NumberColumn("Forks", help="Number of forks", width="small"),
            "Open Issues": st.column_config.NumberColumn("Open Issues", help="Number of open issues", width="small"),
            "Private": st.column_config.TextColumn("Visibility", help="Repository visibility", width="small"),
            "Last Push": st.column_config.TextColumn("Last Push", help="Date of last push", width="small"),
            "Language": st.column_config.TextColumn("Language", help="Primary language", width="small"),
        },
        column_order=["Name", "Private", "Stars", "Forks", "Open Issues", "Language", "Last Push", "URL"],
    )

