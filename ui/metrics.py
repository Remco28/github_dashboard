from typing import Optional

import plotly.graph_objects as go
import streamlit as st

from models.github_types import RepoSummary


def render_stat_cards(repo_summaries: list[RepoSummary]) -> None:
    """Render metrics cards showing repository statistics."""
    if not repo_summaries:
        st.info("No repositories to display.")
        return

    total_repos = len(repo_summaries)
    private_count = sum(1 for repo in repo_summaries if repo.private)
    public_count = total_repos - private_count
    archived_count = sum(1 for repo in repo_summaries if repo.archived)
    languages_count = len(set(repo.language for repo in repo_summaries if repo.language))

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("Total Repositories", total_repos, help="Total number of repositories")

    with col2:
        st.metric("Private", private_count, help="Number of private repositories")

    with col3:
        st.metric("Public", public_count, help="Number of public repositories")

    with col4:
        st.metric("Archived", archived_count, help="Number of archived repositories")

    with col5:
        st.metric("Languages", languages_count, help="Number of different programming languages")


def render_progress_circle(percent: int, *, size: int = 90, thickness: int = 10, color: str = "#64b5f6", key: Optional[str] = None) -> None:
    """Render a circular progress indicator with centered percentage."""
    fig = go.Figure(data=[
        go.Pie(
            values=[percent, 100 - percent],
            hole=.7,
            marker=dict(colors=[color, "#f0f0f0"], line=dict(width=0)),
            textinfo='none',
            hoverinfo='skip',
            showlegend=False,
            direction='clockwise',
            sort=False,
        )
    ])

    fig.add_annotation(
        text=f"{percent}%",
        x=0.5,
        y=0.5,
        font_size=16,
        font_color="#333333",
        font_weight="bold",
        showarrow=False,
        xref="paper",
        yref="paper",
    )

    fig.update_layout(
        width=size,
        height=size,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False}, key=key or f"prog-{percent}-{size}-{thickness}")

