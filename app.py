import streamlit as st
import time
from config.settings import get_settings
from services.cache import cached_list_user_repos
from services.github_client import to_repo_summary
from services.analytics import filter_repos, languages_set
from ui.components import render_stat_cards, render_repo_table

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