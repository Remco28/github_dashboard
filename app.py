import time
from datetime import datetime, timedelta, timezone

import streamlit as st

from config.settings import get_settings
from services.analytics import (
    commits_over_time,
    commits_per_repo,
    filter_repos,
    heatmap_counts,
    language_distribution,
    languages_set,
)
from services.cache import (
    cache_metrics,
    cache_stats,
    cached_fetch_features,
    cached_list_repo_commits,
    cached_list_user_repos,
    clear_cache,
)
from services.errors import RateLimitError
from services.github_client import to_repo_summary
from services.features import parse_features
from ui.charts import render_commits_bar, render_heatmap, render_language_pie, render_trend_line
from ui.checklists import (
    render_aggregate,
    render_missing_features_guidance,
    render_repo_features,
)
from ui.controls import (
    render_repo_selector_with_search,
    render_settings_help,
)
from ui.tables import render_repo_table
from ui.metrics import render_stat_cards
from ui.headers import render_section_header
from ui.styles import inject_global_styles, inject_header_deploy_hider
from ui.branding import render_app_title
from ui.notifications import (
    render_cache_info,
    render_error,
    render_last_updated,
    render_section_error,
)

st.set_page_config(
    page_title="GITHUB DASHBOARD",
    page_icon="",
    layout="wide",
    menu_items=None
)

## Global styles and header tweaks
inject_global_styles()
inject_header_deploy_hider()

def main():
    # Custom title with logo below
    render_app_title()

    try:
        # Load configuration
        settings = get_settings()

        # Sidebar logo (centered)
        col1, col2, col3 = st.sidebar.columns([1, 2, 1])
        with col2:
            st.sidebar.image("media/remco28_github.png", width='stretch')

        # Sidebar for filters
        st.sidebar.header("Filters")

        # Handle refresh functionality
        refresh_pressed = st.sidebar.button("Refresh", help="Refresh repository data")

        # Cache controls (need to be defined early for cache_bust calculation)
        bypass_cache = st.sidebar.checkbox(
            "Bypass Cache",
            help="Force fresh data fetches, ignoring cached data"
        )

        # Use cache_bust parameter to bypass cache when refresh is pressed or bypass is checked
        cache_bust = str(time.time()) if (refresh_pressed or bypass_cache) else None

        # Repository fetch with error handling
        raw_repos = []
        repo_fetch_time = None

        try:
            # Show loading state
            with st.spinner("Loading repositories..."):
                # Fetch repositories
                raw_repos = cached_list_user_repos(
                    settings.github_username,
                    settings.github_token,
                    cache_bust
                )
                repo_fetch_time = time.time()
        except Exception as e:
            render_error(e)
            st.info("Using cached data if available, or showing empty state.")
            # Try to get cached data without cache bust
            try:
                raw_repos = cached_list_user_repos(
                    settings.github_username,
                    settings.github_token,
                    None
                )
            except Exception:
                raw_repos = []

        # Convert to RepoSummary objects
        all_repo_summaries = [to_repo_summary(repo) for repo in raw_repos]

        # Get available languages for filter
        available_languages = languages_set(all_repo_summaries)

        # Sidebar filter controls
        selected_languages = st.sidebar.multiselect(
            "Languages",
            options=available_languages,
            help="Filter repositories by programming language"
        )

        visibility_option = st.sidebar.radio(
            "Visibility",
            ["All", "Public", "Private"],
            index=0,
            help="Filter by repository visibility"
        )

        activity_days = st.sidebar.slider(
            "Activity Window (days)",
            min_value=7,
            max_value=365,
            value=90,
            help="Show repositories with activity in the last N days"
        )

        # Visualization controls
        st.sidebar.markdown("---")
        st.sidebar.header("Visualizations")

        max_repos = st.sidebar.selectbox(
            "Max Repositories for Charts",
            options=[5, 10, 20, 50, 100],
            index=1,
            help="Number of repositories to analyze for commit-based charts"
        )

        # Features processing controls
        st.sidebar.markdown("---")
        st.sidebar.header("Features")

        features_limit = st.sidebar.slider(
            "Features Processing Limit",
            min_value=10,
            max_value=100,
            value=20,
            help="Maximum number of repositories to process for features analysis"
        )


        # Cache controls (continued)
        st.sidebar.markdown("---")
        st.sidebar.header("Cache Controls")

        # Toggle for showing cache stats
        show_cache_stats = getattr(st.sidebar, "toggle", st.sidebar.checkbox)(
            "Show Stats", help="Display cache stats", key="show_cache_stats"
        )

        if st.sidebar.button("Clear Cache"):
            clear_cache()
            st.sidebar.success("Cache cleared!")
            st.rerun()

        # Show cache stats with telemetry only if toggle is enabled
        if show_cache_stats:
            stats = cache_stats()
            telemetry = cache_metrics()
            merged_stats = {**stats, **telemetry}
            render_cache_info(merged_stats, location="sidebar")

        # Settings help panel
        render_settings_help(settings.github_username)

        # Clear filters button
        if st.sidebar.button("Clear All Filters"):
            st.rerun()

        # Ensure inline filter has a default session value ready for downstream calculations.
        if "table_filter_query" not in st.session_state:
            st.session_state["table_filter_query"] = ""
        table_filter_query_value = st.session_state.get("table_filter_query", "")

        # Calculate time window for commit-based charts
        # Use timezone-aware UTC per Python 3.12+ deprecation guidance
        until_dt = datetime.now(timezone.utc)
        since_dt = until_dt - timedelta(days=activity_days)
        since_iso = since_dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')
        until_iso = until_dt.replace(microsecond=0).isoformat().replace('+00:00', 'Z')

        # Apply filters
        include_private = None
        if visibility_option == "Private":
            include_private = True
        elif visibility_option == "Public":
            include_private = False

        filter_query_clean = table_filter_query_value.strip() if table_filter_query_value else ""
        filtered_repos = filter_repos(
            all_repo_summaries,
            languages=set(selected_languages) if selected_languages else None,
            include_private=include_private,
            activity_days=activity_days,
            query=filter_query_clean or None
        )

        # Display summary statistics using components
        render_stat_cards(filtered_repos)

        # Show last updated info
        render_last_updated(repo_fetch_time, "Repository data")

        # Display repositories table using components
        table_section = st.container()
        with table_section:
            st.text_input(
                "Filter repositories by name",
                placeholder="Type part of a repository name...",
                key="table_filter_query",
                help="Filter applies to the table plus charts and Features sections.",
            )

            filter_query_display = st.session_state.get("table_filter_query", "").strip()

            render_repo_table(
                filtered_repos,
                filter_query=filter_query_display or None,
            )

        # Show filter summary
        if len(filtered_repos) != len(all_repo_summaries):
            filters = []
            if selected_languages:
                filters.append(f'Languages: {", ".join(selected_languages)}')
            if visibility_option != 'All':
                filters.append(f'Visibility: {visibility_option}')
            if activity_days != 90:
                filters.append(f'Activity: {activity_days} days')
            if filter_query_display:
                filters.append(f'Name filter: "{filter_query_display}"')

            filter_summary = ""
            if filters:
                filter_summary = f"(filtered by: {', '.join(filters)})"

            st.info(f"Showing {len(filtered_repos)} of {len(all_repo_summaries)} repositories {filter_summary}")
        else:
            st.info(f"Showing all {len(all_repo_summaries)} repositories")

        # Visualizations Section
        st.markdown("---")
        with st.container():
            render_section_header("Visualizations", level='h2', accent='blue')

            if filtered_repos:
                # Refresh button for charts
                charts_refresh_pressed = st.button("Refresh Charts", key="charts_refresh", help="Refresh chart data bypassing cache")
                charts_cache_bust = str(time.time()) if charts_refresh_pressed else None

                # Create responsive 2x2 chart layout
                col1, col2 = st.columns(2)

                with col1:
                    # Language Distribution Pie Chart
                    lang_dist = language_distribution(filtered_repos)
                    render_language_pie(lang_dist)

                    # Commits Over Time - Default to Weekly
                    if "trend_freq" not in st.session_state:
                        st.session_state["trend_freq"] = "Weekly"

                    current_trend_freq = st.session_state.get("trend_freq", "Weekly")
                    freq = "D" if current_trend_freq == "Daily" else "W"
                    try:
                        trend_data = commits_over_time(
                            filtered_repos,
                            settings.github_token,
                            since_iso,
                            until_iso,
                            max_repos,
                            freq=freq,
                            cache_bust=charts_cache_bust
                        )
                        render_trend_line(trend_data)
                    except RateLimitError as e:
                        render_section_error("Commit Trends", e)
                    except Exception as e:
                        render_section_error("Commit Trends", e)

                    # Place the Trend Granularity control below the chart for visual consistency
                    st.radio(
                        "Trend Granularity",
                        ["Daily", "Weekly"],
                        index=1,  # Default to Weekly
                        key="trend_freq",
                        help="Choose daily or weekly aggregation for the trend chart",
                        horizontal=True
                    )

                with col2:
                    # Commits per Repository Bar Chart
                    try:
                        commits_data = commits_per_repo(filtered_repos, settings.github_token, since_iso, until_iso, max_repos, cache_bust=charts_cache_bust)
                        render_commits_bar(commits_data)
                    except RateLimitError as e:
                        render_section_error("Commits per Repository", e)
                    except Exception as e:
                        render_section_error("Commits per Repository", e)

                    # Activity Heatmap
                    try:
                        heatmap_data = heatmap_counts(filtered_repos, settings.github_token, since_iso, until_iso, max_repos, cache_bust=charts_cache_bust)
                        render_heatmap(heatmap_data)
                    except RateLimitError as e:
                        render_section_error("Activity Heatmap", e)
                    except Exception as e:
                        render_section_error("Activity Heatmap", e)

            else:
                st.info("No repositories available for visualization. Try adjusting your filters.")

        # Features Section
        st.markdown("---")
        with st.container():
            render_section_header("Features", level='h2', accent='gold')

            if filtered_repos:
                # Refresh button for Features
                features_refresh_pressed = st.button("Refresh Features", key="features_refresh", help="Refresh features data bypassing cache")
                features_cache_bust = str(time.time()) if features_refresh_pressed else None

                with st.spinner("Loading features data..."):
                    # Sort repos by recent activity (pushed_at descending) and limit processing
                    sorted_repos = sorted(filtered_repos, key=lambda r: r.pushed_at or "", reverse=True)
                    repos_to_process = sorted_repos[:features_limit]

                    # Fetch FEATURES.md files
                    features_docs = {}
                    missing_files_count = 0

                    # Add progress indicator for large processing sets
                    progress_bar = None
                    if len(repos_to_process) > 20:
                        progress_bar = st.progress(0, text="Processing FEATURES.md files...")
                        st.info(f"Processing {len(repos_to_process)} repositories for features analysis...")

                    for i, repo in enumerate(repos_to_process):
                        owner, name = repo.full_name.split('/', 1)

                        try:
                            md_content = cached_fetch_features(owner, name, settings.github_token, features_cache_bust)
                            if md_content:
                                doc = parse_features(md_content, repo.full_name)
                                features_docs[repo.full_name] = doc
                            else:
                                missing_files_count += 1
                        except RateLimitError:
                            # Skip this repo due to rate limiting, but don't show individual errors
                            missing_files_count += 1
                            if len(repos_to_process) > 20:
                                st.warning("Rate limit encountered during features processing. Some repositories may be skipped.")
                        except Exception:
                            # Skip this repo due to other errors
                            missing_files_count += 1

                        # Update progress bar
                        if progress_bar and len(repos_to_process) > 20:
                            progress = (i + 1) / len(repos_to_process)
                            progress_bar.progress(progress, text=f"Processing FEATURES.md files... ({i + 1}/{len(repos_to_process)})")

                    # Complete progress bar
                    if progress_bar:
                        progress_bar.empty()

                    # Extract features by repo for aggregate view
                    features_by_repo = {
                        repo_name: doc.features
                        for repo_name, doc in features_docs.items()
                    }

                    # Render aggregate view
                    render_aggregate(features_by_repo)

                    # Store features_docs for use in separate Feature Details section
                    st.session_state['features_docs'] = features_docs

                    # Show guidance for missing files
                    if missing_files_count > 0:
                        render_missing_features_guidance(missing_files_count)

                    # Processing summary
                    processed_count = len(repos_to_process)
                    total_filtered = len(filtered_repos)

                    if processed_count < total_filtered:
                        st.info(
                            f"Processed {processed_count} of {total_filtered} repositories. "
                            f"Repositories are sorted by recent activity and limited to {features_limit} for performance."
                        )

            else:
                st.info("No repositories available for features analysis. Try adjusting your filters.")
                # Clear session state if no repos
                st.session_state['features_docs'] = {}

        # Feature Details Section (separate from Features)
        st.markdown("---")
        with st.container():
            render_section_header("Feature Details", level='h2', accent='green')

            # Get features_docs from session state
            features_docs = st.session_state.get('features_docs', {})

            if features_docs:
                selected_repo = render_repo_selector_with_search(
                    options=list(features_docs.keys()),
                    key="features_repo_selector",
                    help_text="Choose a repository to see its FEATURES.md"
                )

                if selected_repo:
                    render_repo_features(features_docs[selected_repo])
            else:
                st.info("No feature data available. Please load Features data first.")

    except RuntimeError as e:
        st.error(f"Configuration Error: {e}")
        st.info(
            "Please ensure your `.env` file contains valid `GITHUB_TOKEN` and "
            "`GITHUB_USERNAME` values. See `.env.example` for the required format."
        )

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.info("Please check your GitHub token permissions and network connection.")


if __name__ == "__main__":
    main()
