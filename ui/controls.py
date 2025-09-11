import streamlit as st


def render_repo_selector_with_search(options: list[str], key: str, help_text: str) -> str | None:
    """Render an enhanced repository selector with search capability for large lists."""
    if len(options) <= 20:
        return st.selectbox(
            "Select repository to view tasks:",
            options=options,
            key=key,
            help=help_text,
        )

    search_query = st.text_input(
        "Search repositories:",
        placeholder="Type to filter repositories...",
        key=f"{key}_search",
        help="Filter repositories by name (case-insensitive)",
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
        help=help_text,
    )


def render_settings_help(username: str) -> None:
    """Render settings help panel in sidebar."""
    with st.sidebar.expander("Settings Help"):
        st.write(f"GitHub Username: **{username or 'Not set'}**")
        st.write("Token: loaded from environment (not displayed)")

        st.markdown("**Setup Steps:**")
        st.markdown(
            """
            • Create `.env` file with `GITHUB_TOKEN` and `GITHUB_USERNAME`
            • Token needs `repo` scope for private repos, `public_repo` for public only
            • Check `.env.example` for format reference
            • Rate limits: 5000/hour authenticated, 60/hour unauthenticated
            • Use cache controls if hitting rate limits frequently
            """
        )

        st.markdown("**Common Issues:**")
        st.markdown(
            """
            • **Empty repositories:** Check username spelling and token permissions
            • **Authentication errors:** Verify token is valid and has required scopes
            • **Rate limits:** Use "Bypass Cache" sparingly, or wait for reset
            • **Missing data:** Try refreshing or clearing cache
            """
        )

