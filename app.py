import streamlit as st
import time
from datetime import datetime, timedelta
from config.settings import get_settings
from services.cache import cached_list_user_repos
from services.github_client import to_repo_summary
from services.analytics import filter_repos, languages_set, language_distribution, commits_per_repo, commits_over_time, heatmap_counts
from ui.components import render_stat_cards, render_repo_table
from ui.charts import render_language_pie, render_commits_bar, render_trend_line, render_heatmap

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
        
        # Use cache_bust parameter to bypass cache when refresh is pressed
        cache_bust = str(time.time()) if refresh_pressed else None
        
        # Show loading state
        with st.spinner("Loading repositories..."):
            # Fetch repositories
            raw_repos = cached_list_user_repos(
                settings.github_username, 
                settings.github_token, 
                cache_bust
            )
        
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
            options=[5, 10, 20],
            index=1,
            help="Number of repositories to analyze for commit-based charts"
        )
        
        # Clear filters button
        if st.sidebar.button("🗑️ Clear All Filters"):
            st.rerun()
        
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
            # Calculate time window for commit-based charts
            until_dt = datetime.utcnow()
            since_dt = until_dt - timedelta(days=activity_days)
            since_iso = since_dt.replace(microsecond=0).isoformat() + 'Z'
            until_iso = until_dt.replace(microsecond=0).isoformat() + 'Z'
            
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
                    trend_data = commits_over_time(filtered_repos, settings.github_token, since_iso, until_iso, max_repos)
                    render_trend_line(trend_data)
                except Exception as e:
                    st.warning(f"Unable to fetch commit trend data: {str(e)[:100]}...")
                    st.info("This chart requires API access to commit data.")
            
            with col2:
                # Commits per Repository Bar Chart
                st.subheader("📊 Commits per Repository")
                try:
                    commits_data = commits_per_repo(filtered_repos, settings.github_token, since_iso, until_iso, max_repos)
                    render_commits_bar(commits_data)
                except Exception as e:
                    st.warning(f"Unable to fetch commits per repository: {str(e)[:100]}...")
                    st.info("This chart requires API access to commit data.")
                
                # Activity Heatmap
                st.subheader("🔥 Activity Heatmap")
                try:
                    heatmap_data = heatmap_counts(filtered_repos, settings.github_token, since_iso, until_iso, max_repos)
                    render_heatmap(heatmap_data)
                except Exception as e:
                    st.warning(f"Unable to fetch heatmap data: {str(e)[:100]}...")
                    st.info("This chart requires API access to commit data.")
        
        else:
            st.info("📊 No repositories available for visualization. Try adjusting your filters.")
    
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