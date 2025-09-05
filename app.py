import streamlit as st
import time
from datetime import datetime, timedelta, timezone
from config.settings import get_settings
from services.cache import cached_list_user_repos, cached_list_repo_commits, cached_compute_streaks, clear_cache, cache_stats, cache_metrics
from services.github_client import to_repo_summary
from services.analytics import filter_repos, languages_set, language_distribution, commits_per_repo, commits_over_time, heatmap_counts
from services.cache import cached_fetch_next_steps
from services.next_steps import parse_next_steps
from services.gamification import compute_activity_dates, assign_badges, detect_stale_repos
from services.errors import RateLimitError
from ui.components import render_stat_cards, render_repo_table, render_settings_help
from ui.charts import render_language_pie, render_commits_bar, render_trend_line, render_heatmap
from ui.checklists import render_aggregate, render_repo_next_steps, render_missing_next_steps_guidance
from ui.gamification import render_badges, render_streaks, render_stale_nudges
from ui.notifications import render_error, render_last_updated, render_cache_info, render_section_error

st.set_page_config(
    page_title="GitHub Project Tracker Dashboard",
    page_icon="📊",
    layout="wide"
)


def main():
    st.title("📊 GitHub Project Tracker Dashboard")
    
    try:
        # Load configuration
        settings = get_settings()
        
        # Sidebar for filters
        st.sidebar.header("🎛️ Filters")
        
        # Handle refresh functionality
        refresh_pressed = st.sidebar.button("🔄 Refresh", help="Refresh repository data")
        
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
        
        search_query = st.sidebar.text_input(
            "Search",
            placeholder="Repository name...",
            help="Search repositories by name (case-insensitive)"
        )
        
        # Visualization controls
        st.sidebar.markdown("---")
        st.sidebar.header("📊 Visualizations")
        
        max_repos = st.sidebar.selectbox(
            "Max Repositories for Charts",
            options=[5, 10, 20, 50, 100],
            index=1,
            help="Number of repositories to analyze for commit-based charts"
        )
        
        stale_threshold = st.sidebar.slider(
            "Stale Threshold (days)",
            min_value=7,
            max_value=180,
            value=30,
            help="Repositories without pushes for this many days are considered stale"
        )
        
        
        # Cache controls (continued)
        st.sidebar.markdown("---")
        st.sidebar.header("💾 Cache Controls")
        
        if st.sidebar.button("🧹 Clear Cache"):
            clear_cache()
            st.sidebar.success("Cache cleared!")
            st.rerun()
        
        # Show cache stats with telemetry
        stats = cache_stats()
        telemetry = cache_metrics()
        merged_stats = {**stats, **telemetry}
        render_cache_info(merged_stats)
        
        # Settings help panel
        render_settings_help(settings.github_username)
        
        # Clear filters button
        if st.sidebar.button("🗑️ Clear All Filters"):
            st.rerun()
        
        # Calculate time window for commit-based charts (used in Visualizations and Motivation)
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

        filtered_repos = filter_repos(
            all_repo_summaries,
            languages=set(selected_languages) if selected_languages else None,
            include_private=include_private,
            activity_days=activity_days,
            query=search_query.strip() if search_query.strip() else None
        )
        
        # Display summary statistics using components
        render_stat_cards(filtered_repos)
        
        # Show last updated info
        render_last_updated(repo_fetch_time, "Repository data")
        
        # Add some spacing
        st.markdown("---")
        
        # Display repositories table using components
        render_repo_table(filtered_repos)
        
        # Show filter summary
        if len(filtered_repos) != len(all_repo_summaries):
            st.info(
                f"Showing {len(filtered_repos)} of {len(all_repo_summaries)} repositories "
                f"(filtered by: {', '.join([f for f in [
                    f'Languages: {", ".join(selected_languages)}' if selected_languages else None,
                    f'Visibility: {visibility_option}' if visibility_option != 'All' else None,
                    f'Activity: {activity_days} days' if activity_days != 90 else None,
                    f'Search: "{search_query}"' if search_query.strip() else None
                ] if f])})")
        else:
            st.info(f"Showing all {len(all_repo_summaries)} repositories")
        
        # Visualizations Section
        st.markdown("---")
        st.header("📊 Visualizations")

        if filtered_repos:
            # Refresh button for charts
            charts_refresh_pressed = st.button("🔄 Refresh Charts", key="charts_refresh", help="Refresh chart data bypassing cache")
            charts_cache_bust = str(time.time()) if charts_refresh_pressed else None

            # Create two columns for charts
            col1, col2 = st.columns(2)

            with col1:
                # Language Distribution Pie Chart
                st.subheader("🎯 Language Distribution")
                lang_dist = language_distribution(filtered_repos)
                render_language_pie(lang_dist)

                # Commits Over Time
                st.subheader("📈 Commit Trends")
                try:
                    trend_data = commits_over_time(filtered_repos, settings.github_token, since_iso, until_iso, max_repos, cache_bust=charts_cache_bust)
                    render_trend_line(trend_data)
                except RateLimitError as e:
                    render_section_error("Commit Trends", e)
                except Exception as e:
                    render_section_error("Commit Trends", e)

            with col2:
                # Commits per Repository Bar Chart
                st.subheader("📊 Commits per Repository")
                try:
                    commits_data = commits_per_repo(filtered_repos, settings.github_token, since_iso, until_iso, max_repos, cache_bust=charts_cache_bust)
                    render_commits_bar(commits_data)
                except RateLimitError as e:
                    render_section_error("Commits per Repository", e)
                except Exception as e:
                    render_section_error("Commits per Repository", e)

                # Activity Heatmap
                st.subheader("🔥 Activity Heatmap")
                try:
                    heatmap_data = heatmap_counts(filtered_repos, settings.github_token, since_iso, until_iso, max_repos, cache_bust=charts_cache_bust)
                    render_heatmap(heatmap_data)
                except RateLimitError as e:
                    render_section_error("Activity Heatmap", e)
                except Exception as e:
                    render_section_error("Activity Heatmap", e)

        else:
            st.info("📊 No repositories available for visualization. Try adjusting your filters.")
        
        # NEXT_STEPS Section
        st.markdown("---")
        st.header("📝 Project Tasks (NEXT_STEPS)")

        if filtered_repos:
            # Refresh button for NEXT_STEPS
            next_steps_refresh_pressed = st.button("🔄 Refresh NEXT_STEPS", key="next_steps_refresh", help="Refresh NEXT_STEPS data bypassing cache")
            next_steps_cache_bust = str(time.time()) if next_steps_refresh_pressed else None

            with st.spinner("Loading NEXT_STEPS data..."):
                # Limit to first 20 repos to keep API calls bounded
                repos_to_process = filtered_repos[:20]

                # Fetch NEXT_STEPS.md files
                next_steps_docs = {}
                missing_files_count = 0

                for repo in repos_to_process:
                    owner, name = repo.full_name.split('/', 1)

                    try:
                        md_content = cached_fetch_next_steps(owner, name, settings.github_token, next_steps_cache_bust)
                        if md_content:
                            doc = parse_next_steps(md_content, repo.full_name)
                            next_steps_docs[repo.full_name] = doc
                        else:
                            missing_files_count += 1
                    except RateLimitError:
                        # Skip this repo due to rate limiting, but don't show individual errors
                        missing_files_count += 1
                    except Exception:
                        # Skip this repo due to other errors
                        missing_files_count += 1
                
                # Extract tasks by repo for aggregate view
                tasks_by_repo = {
                    repo_name: doc.tasks 
                    for repo_name, doc in next_steps_docs.items()
                }
                
                # Render aggregate view
                render_aggregate(tasks_by_repo)
                
                # Repository selector for detailed view
                if next_steps_docs:
                    st.markdown("---")
                    st.subheader("📋 Repository Details")
                    
                    selected_repo = st.selectbox(
                        "Select repository to view tasks:",
                        options=list(next_steps_docs.keys()),
                        key="next_steps_repo_selector",
                        help="Choose a repository to see its NEXT_STEPS.md tasks"
                    )
                    
                    if selected_repo:
                        render_repo_next_steps(next_steps_docs[selected_repo])
                
                # Show guidance for missing files
                if missing_files_count > 0:
                    st.markdown("---")
                    render_missing_next_steps_guidance(missing_files_count)
                
                # Processing summary
                processed_count = len(repos_to_process)
                total_filtered = len(filtered_repos)
                
                if processed_count < total_filtered:
                    st.info(
                        f"📊 Processed {processed_count} of {total_filtered} repositories. "
                        f"To improve performance, only the first 20 repositories are analyzed for NEXT_STEPS."
                    )
        
        else:
            st.info("📝 No repositories available for NEXT_STEPS analysis. Try adjusting your filters.")
        
        # Motivation Section (Streaks & Badges)
        st.markdown("---")
        st.header("🏆 Motivation")

        if filtered_repos:
            # Refresh button for Motivation
            motivation_refresh_pressed = st.button("🔄 Refresh Motivation", key="motivation_refresh", help="Refresh motivation data bypassing cache")
            motivation_cache_bust = str(time.time()) if motivation_refresh_pressed else None

            try:
                with st.spinner("Computing activity streaks and badges..."):
                    # Use same bounded repo set as visualizations
                    repos_to_analyze = filtered_repos[:max_repos]

                    # Fetch commit data for streak computation
                    commits_by_repo = {}
                    rate_limited = False

                    for repo in repos_to_analyze:
                        owner, name = repo.full_name.split('/', 1)

                        try:
                            commits = cached_list_repo_commits(owner, name, settings.github_token, since_iso, until_iso, motivation_cache_bust)
                            commits_by_repo[repo.full_name] = commits
                        except RateLimitError:
                            rate_limited = True
                            commits_by_repo[repo.full_name] = []
                        except Exception:
                            # Skip repos that fail to fetch
                            commits_by_repo[repo.full_name] = []
                    
                    # Compute activity dates and streaks
                    activity_dates = compute_activity_dates(commits_by_repo)
                    
                    # Use cached streak computation with hashable tuple
                    streaks = cached_compute_streaks(tuple(sorted(activity_dates)), until_iso[:10])
                    
                    # Calculate total commits and assign badges
                    total_commits = sum(len(commits) for commits in commits_by_repo.values())
                    badges = assign_badges(streaks, total_commits)
                    
                    # Render streak stats
                    st.subheader("🔥 Activity Streaks")
                    render_streaks(streaks)
                    
                    # Render badges
                    st.subheader("🏅 Achievements")
                    render_badges(badges)
                    
                    # Show analysis summary
                    analyzed_count = len(repos_to_analyze)
                    total_filtered = len(filtered_repos)
                    
                    if rate_limited:
                        st.warning("⏱️ Some repositories were skipped due to rate limiting. Results may be incomplete.")
                    
                    if analyzed_count < total_filtered:
                        st.info(
                            f"📊 Streak analysis based on {analyzed_count} of {total_filtered} repositories "
                            f"(limited by 'Max Repositories for Charts' setting)."
                        )
                    else:
                        st.info(f"📊 Streak analysis based on all {analyzed_count} repositories.")
            
            except RateLimitError as e:
                render_section_error("Motivation", e)
            except Exception as e:
                render_section_error("Motivation", e)
        
        else:
            st.info("🏆 No repositories available for motivation analysis. Try adjusting your filters.")
        
        # Nudges Section (Stale Repositories)  
        st.markdown("---")
        st.header("🚨 Nudges")
        
        if filtered_repos:
            try:
                with st.spinner("Detecting stale repositories..."):
                    # Detect stale repositories from all filtered repos
                    stale_repos = detect_stale_repos(filtered_repos, stale_threshold)
                    
                    # Render stale repository nudges
                    render_stale_nudges(stale_repos, limit=5)
            except Exception as e:
                render_section_error("Nudges", e)
        
        else:
            st.info("🚨 No repositories available for nudge analysis. Try adjusting your filters.")
    
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
