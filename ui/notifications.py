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


def render_cache_info(cache_stats: dict) -> None:
    """
    Render cache statistics information.
    
    Args:
        cache_stats: Dictionary containing cache statistics
    """
    count = cache_stats.get("count", 0)
    
    if count == 0:
        st.info("💾 Cache is empty")
        return
    
    # Show basic cache info
    keys = cache_stats.get("keys", [])
    keys_display = ", ".join(keys[:3])  # Show first 3 function names
    if len(keys) > 3:
        keys_display += f" and {len(keys) - 3} more"
    
    earliest = cache_stats.get("earliest_expiry")
    latest = cache_stats.get("latest_expiry")
    
    info_text = f"💾 **Cache Status:** {count} active entries"
    
    if keys:
        info_text += f"\n📊 **Cached functions:** {keys_display}"
    
    if earliest and latest:
        try:
            now = time.time()
            earliest_mins = int((earliest - now) / 60)
            latest_mins = int((latest - now) / 60)
            
            if earliest_mins <= 0:
                info_text += f"\n⏰ **Expiry:** Some entries expiring soon"
            else:
                info_text += f"\n⏰ **Expiry:** {earliest_mins}-{latest_mins} minutes remaining"
        except (OSError, ValueError):
            pass
    
    st.info(info_text)


def render_loading_placeholder(message: str = "Loading...") -> None:
    """
    Render a consistent loading placeholder.
    
    Args:
        message: Loading message to display
    """
    with st.spinner(message):
        # Create a placeholder that can be replaced when loading completes
        placeholder = st.empty()
        return placeholder


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