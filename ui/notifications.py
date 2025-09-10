import streamlit as st
import time
from typing import Optional
from services.errors import AuthError, RateLimitError, NotFoundError, GitHubApiError, format_reset_time


def render_error(e: Exception) -> None:
    """
    Render consistent error messages based on exception type.
    
    Args:
        e: Exception to render (GitHub API errors or generic exceptions)
    """
    if isinstance(e, AuthError):
        st.error(
            "🔐 **Authentication Failed**\n\n"
            "Your GitHub token is invalid or lacks necessary permissions. "
            "Please check your `.env` file and ensure your `GITHUB_TOKEN` is valid and has the required scopes.\n\n"
            "💡 **How to fix:**\n"
            "1. Generate a new personal access token at [GitHub Settings](https://github.com/settings/tokens)\n"
            "2. Ensure it has 'repo' scope for private repositories or 'public_repo' for public only\n"
            "3. Update your `.env` file with the new token\n"
            "4. Restart the application"
        )
    
    elif isinstance(e, RateLimitError):
        reset_time_str = format_reset_time(e.reset_epoch)
        st.warning(
            f"⏱️ **Rate Limit Exceeded**\n\n"
            f"You've reached GitHub's API rate limit. "
            f"Limits reset at **{reset_time_str}**.\n\n"
            "💡 **What to do:**\n"
            "- Wait for the rate limit to reset\n"
            "- Use cached data if available\n"
            "- Consider reducing the number of repositories analyzed"
        )
    
    elif isinstance(e, NotFoundError):
        st.info(
            "🔍 **Resource Not Found**\n\n"
            "The requested resource (repository, file, or data) was not found. "
            "This might be expected behavior for optional features."
        )
    
    elif isinstance(e, GitHubApiError):
        st.warning(
            f"⚠️ **GitHub API Error ({e.status})**\n\n"
            "GitHub API returned an error. Some data may be temporarily unavailable.\n\n"
            "💡 **Try:**\n"
            "- Refreshing the data\n"
            "- Checking your network connection\n"
            "- Bypassing cache for fresh data"
        )
    
    else:
        st.warning(
            "🌐 **Network Error**\n\n"
            "A network or connection error occurred. Please check your internet connection and try again.\n\n"
            "💡 **Try:**\n"
            "- Refreshing the page\n"
            "- Checking your network connection\n"
            "- Bypassing cache for a fresh request"
        )


def render_last_updated(ts: Optional[float], label: str = "Data") -> None:
    """
    Render a 'last updated' timestamp indicator.
    
    Args:
        ts: Unix timestamp of last update, or None if unknown
        label: Label for what was updated (e.g., "Data", "Repositories")
    """
    if ts is None:
        st.caption(f"🕐 {label} last updated: Unknown")
        return
    
    try:
        # Format as local time
        local_time = time.localtime(ts)
        time_str = time.strftime("%Y-%m-%d %H:%M:%S", local_time)
        
        # Calculate time ago
        now = time.time()
        seconds_ago = int(now - ts)
        
        if seconds_ago < 60:
            ago_str = f"{seconds_ago} seconds ago"
        elif seconds_ago < 3600:
            ago_str = f"{seconds_ago // 60} minutes ago"
        elif seconds_ago < 86400:
            ago_str = f"{seconds_ago // 3600} hours ago"
        else:
            ago_str = f"{seconds_ago // 86400} days ago"
        
        st.caption(f"🕐 {label} last updated: {time_str} ({ago_str})")
    
    except (OSError, ValueError):
        st.caption(f"🕐 {label} last updated: Invalid timestamp")


def render_cache_info(cache_stats: dict, location: str = "main") -> None:
    """
    Render cache statistics information using structured metrics display.

    Args:
        cache_stats: Dictionary containing cache statistics
        location: Where to render the info ("main" or "sidebar")
    """
    dst = st.sidebar if location == "sidebar" else st
    count = cache_stats.get("count", 0)

    if count == 0:
        dst.info("💾 Cache is empty")
        return

    # Main cache entries metric
    dst.metric(
        label="Cache Entries",
        value=count,
        help="Number of active cached function results"
    )

    # Performance metrics if telemetry available
    if "total_hits" in cache_stats:
        total_hits = cache_stats["total_hits"]
        total_misses = cache_stats["total_misses"]
        hit_rate = cache_stats["hit_rate"]
        
        dst.metric(
            label="Cache Hit Rate",
            value=f"{hit_rate:.1%}",
            delta=f"{total_hits} hits, {total_misses} misses",
            help="Percentage of requests served from cache vs. requiring fresh API calls"
        )

    # Expiry information as caption
    earliest = cache_stats.get("earliest_expiry")
    latest = cache_stats.get("latest_expiry")
    
    if earliest and latest:
        try:
            now = time.time()
            earliest_mins = int((earliest - now) / 60)
            latest_mins = int((latest - now) / 60)

            if earliest_mins <= 0:
                dst.caption("Some entries expiring soon")
            else:
                dst.caption(f"Expires in {earliest_mins}-{latest_mins} minutes")
        except (OSError, ValueError):
            pass

    # Detailed information in expander
    with dst.expander("🔍 Cache Details"):
        keys = cache_stats.get("keys", [])
        if keys:
            keys_display = ", ".join(keys[:5])  # Show first 5 function names
            if len(keys) > 5:
                keys_display += f" + {len(keys) - 5} more"
            st.write(f"**Cached functions:** {keys_display}")
        
        # Top performers if available
        if "total_hits" in cache_stats:
            top_3 = cache_stats.get("top_3_by_hits", [])
            if top_3:
                st.write("**Top performers:**")
                for name, hits in top_3:
                    st.write(f"• {name}: {hits} hits")


def render_loading_placeholder(message: str = "Loading...") -> None:
    """
    Render a consistent loading spinner (visual side-effect only).

    Args:
        message: Loading message to display
    """
    with st.spinner(message):
        # Spinner context only; no value returned
        pass


def render_section_error(section_name: str, error: Exception, show_details: bool = False) -> None:
    """
    Render an error state for a specific dashboard section.
    
    Args:
        section_name: Name of the section that encountered an error
        error: The exception that occurred
        show_details: Whether to show detailed error information
    """
    with st.container():
        st.warning(f"⚠️ **{section_name} Section Unavailable**")
        
        if isinstance(error, RateLimitError):
            reset_time = format_reset_time(error.reset_epoch)
            st.info(
                f"This section is temporarily disabled due to rate limiting. "
                f"Service resumes at {reset_time}."
            )
        elif isinstance(error, AuthError):
            st.info("This section requires authentication. Please check your GitHub token configuration.")
        else:
            st.info("This section encountered an error and is temporarily unavailable.")
        
        if show_details:
            with st.expander("🔍 Error Details"):
                st.text(str(error))
