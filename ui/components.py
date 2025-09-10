import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from models.github_types import RepoSummary
import base64


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


def get_logo_base64() -> str:
    """Load and encode the app logo image as base64."""
    try:
        with open("media/logo_trans_blue_med.png", "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""


def inject_global_styles() -> None:
    """Inject global CSS styles used across the app."""
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;600&family=Crimson+Text:ital,wght@0,400;1,400&display=swap');
    /* Hide Streamlit menu/deploy controls (and variants) */
    [data-testid="stMenu"] { display: none !important; }
    [data-testid="stDeployButton"] { display: none !important; }
    .stDeployButton { display: none !important; }
    header button[title*="Deploy" i] { display: none !important; }
    header [aria-label*="Deploy" i] { display: none !important; }
    header a[href*="share.streamlit.io"] { display: none !important; }
    header a[href*="deploy" i] { display: none !important; }
    /* Additional fallbacks for local dev variants */
    header [data-testid="stHeaderActionButton"] { display: none !important; }
    header [data-testid*="DeployButton" i] { display: none !important; }
    /* Older Streamlit IDs */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Additional header menu variants */
    header [aria-label*="menu" i] { display: none !important; }
    header [data-testid*="Menu" i] { display: none !important; }

    /* Plotly chart cards */
    [data-testid="stPlotlyChart"] {
        border: 1px solid rgba(0,0,0,0.08);
        border-radius: 10px;
        background: #fff;
        padding: 12px;
        margin-bottom: 16px;
        box-shadow: 0 1px 2px rgba(0,0,0,0.04);
        box-sizing: border-box;
        max-width: 100%;
        overflow: hidden; /* keep contents within rounded border */
    }
    [data-testid="stPlotlyChart"] .js-plotly-plot,
    [data-testid="stPlotlyChart"] .plot-container {
        max-width: 100% !important;
        width: 100% !important;
    }
    [data-testid="stPlotlyChart"] .modebar {
        top: 8px !important;
        bottom: auto !important;
        right: 16px !important; /* consistent top-right placement */
    }

    /* Optional: modest spacing tweaks, avoid header/tooling containers */
    .block-container { padding-top: 0.75rem !important; }

    /* Sidebar padding to avoid slider value clipping */
    .stSidebar .block-container { padding-right: 28px !important; }
    .stSidebar [data-testid="stSlider"] { padding-right: 12px !important; }

    /* DataFrame compact headers and prevent URL column from expanding */
    [data-testid="stDataFrame"] thead th {
        padding: 6px 8px !important;
    }
    [data-testid="stDataFrame"] tbody td {
        padding: 6px 8px !important;
    }
    [data-testid="stDataFrame"] td, [data-testid="stDataFrame"] th {
        max-width: 100%;
        white-space: nowrap;
        text-overflow: ellipsis;
        overflow: hidden;
    }
    /* Removed forced tight width on last (URL) column to allow wider display */
    /* Note: column-specific alignment tweaks for a leading icon column removed */

    /* Keep the sidebar toggle visible in all states */
    [data-testid="stSidebarCollapseButton"] {
        visibility: visible !important;
        opacity: 1 !important;
    }

    /* Section container styling */
    .gd-section-container {
        border: 1px solid #dfe1e5;
        border-radius: 8px;
        padding: 1.5rem;
        margin-bottom: 1.5rem;
        background: #fff;
        box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.12);
    }

    /* Enhanced Languages dropdown styling */
    .stSidebar [data-testid="stMultiSelect"] {
        border: 1px solid #d1d5db;
        border-radius: 6px;
        background: #f9fafb;
        padding: 2px;
    }
    .stSidebar [data-testid="stMultiSelect"] > div {
        background: #f9fafb;
        border: none;
    }
    .stSidebar [data-testid="stMultiSelect"] input::placeholder {
        color: #6b7280 !important;
        opacity: 1;
    }

    /* Enhanced Search input styling */
    .stSidebar [data-testid="stTextInput"] {
        border: 1px solid #d1d5db;
        border-radius: 6px;
        background: #f9fafb;
        padding: 2px;
    }
    .stSidebar [data-testid="stTextInput"] > div {
        background: #f9fafb;
        border: none;
    }
    .stSidebar [data-testid="stTextInput"] input {
        background: #f9fafb !important;
        border: none !important;
    }
    .stSidebar [data-testid="stTextInput"] input::placeholder {
        color: #6b7280 !important;
        opacity: 1;
    }

    /* Text shadows for statistics metrics */
    [data-testid="stMetricLabel"],
    [data-testid="stMetricValue"] {
        text-shadow: 0 1px 3px rgba(0, 0, 0, 0.2) !important;
    }

    </style>
    """, unsafe_allow_html=True)


def inject_header_deploy_hider() -> None:
    """Inject a small script to hide header Deploy controls in local dev."""
    st.markdown(
        """
        <script>
        document.addEventListener('DOMContentLoaded', function() {
          try {
            const nodes = document.querySelectorAll('header a, header button');
            nodes.forEach(el => {
              const title = el.getAttribute('title') || '';
              const label = el.getAttribute('aria-label') || '';
              const text = (el.textContent || '');
              const hay = (title + ' ' + label + ' ' + text).toLowerCase();
              if (hay.includes('deploy')) {
                el.style.display = 'none';
              }
            });
          } catch (e) { /* no-op */ }
        });
        </script>
        """,
        unsafe_allow_html=True,
    )

def ensure_section_header_styles() -> None:
    """Inject section header styles with :has() hover effects."""
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
      
      .gd-section { margin: 0 0 8px; }
      
      /* Reduce spacing around horizontal rules */
      hr { margin: 8px 0 4px 0 !important; }
      
      .gd-section-title { 
        display: inline; 
        font-family: 'Bebas Neue', sans-serif;
        font-size: 1.5em;
        font-weight: 700; 
        line-height: 1.15; 
        padding: 0 8px 2px; 
        border-radius: 4px; 
        background-image: linear-gradient(var(--gd-accent, #ffd54f), var(--gd-accent, #ffd54f)); 
        background-repeat: no-repeat; 
        background-position: 0 0; 
        background-size: 100% 8px; 
        transition: background-size .45s ease; 
      }
      
      /* Direct hover/focus on section title */
      .gd-section-title:hover, .gd-section-title:focus-visible { 
        background-size: 100% 100%; 
      }
      
      /* CSS :has() rules for section-wide hover - only activate deepest hovered section */
      [data-testid="stVerticalBlock"]
        :is(:hover, :focus-within)
        :has(> [data-testid="stMarkdownContainer"] .gd-section-title)
        :not(:has([data-testid="stVerticalBlock"] :is(:hover, :focus-within) .gd-section-title))
        .gd-section-title {
        background-size: 100% 100%;
      }
      
      /* Fallback for browsers without :has() support */
      .gd-section-title[data-gd-active="true"] { 
        background-size: 100% 100%; 
      }
      
      .gd-section-title:focus-visible { 
        outline: 2px solid var(--gd-accent, #ffd54f); 
        outline-offset: 2px; 
      }
      .gd-accent-gold { --gd-accent: #ffd54f; }
      .gd-accent-blue { --gd-accent: #64b5f6; }
      .gd-accent-green { --gd-accent: #81c784; }
      .gd-accent-red { --gd-accent: #ef9a9a; }
      .gd-accent-purple { --gd-accent: #b39ddb; }
      @media (prefers-reduced-motion: reduce) { 
        .gd-section-title { transition: none; } 
      }
    </style>
    """, unsafe_allow_html=True)
    
    # Progressive enhancement fallback for browsers without :has() support
    st.markdown("""
    <script>
    // Only run fallback if :has() is not supported
    if (!CSS.supports('selector(:has(*))')) {
        console.log('CSS :has() not supported, adding fallback listeners');
        
        // Delegated event listeners on document body
        document.body.addEventListener('mouseover', function(e) {
            const target = e.target.closest('[data-testid="stVerticalBlock"]');
            if (target) {
                const title = target.querySelector('.gd-section-title');
                if (title) {
                    title.setAttribute('data-gd-active', 'true');
                }
            }
        });
        
        document.body.addEventListener('mouseout', function(e) {
            const target = e.target.closest('[data-testid="stVerticalBlock"]');
            if (target) {
                const title = target.querySelector('.gd-section-title');
                if (title) {
                    title.removeAttribute('data-gd-active');
                }
            }
        });
        
        document.body.addEventListener('focusin', function(e) {
            const target = e.target.closest('[data-testid="stVerticalBlock"]');
            if (target) {
                const title = target.querySelector('.gd-section-title');
                if (title) {
                    title.setAttribute('data-gd-active', 'true');
                }
            }
        });
        
        document.body.addEventListener('focusout', function(e) {
            const target = e.target.closest('[data-testid="stVerticalBlock"]');
            if (target) {
                const title = target.querySelector('.gd-section-title');
                if (title) {
                    title.removeAttribute('data-gd-active');
                }
            }
        });
    } else {
        console.log('CSS :has() is supported, using CSS-only approach');
    }
    </script>
    """, unsafe_allow_html=True)
    


def render_section_header(title: str, icon: str | None = None, *, level: str = 'h2', accent: str = 'gold', align: str = 'left') -> None:
    """Render an animated section header with gradient highlight effect.
    
    Args:
        title: Header text
        icon: Optional emoji icon 
        level: HTML heading level ('h2' or 'h3')
        accent: Color accent ('gold', 'blue', or 'green')
        align: Text alignment ('left' or 'center')
    """
    ensure_section_header_styles()
    
    safe_icon = (icon + ' ') if icon else ''
    cls = f"gd-section-title gd-accent-{accent}"
    tag = 'h2' if level == 'h2' else 'h3'
    
    st.markdown(
        f"<{tag} class='gd-section' style='text-align:{align};'><span class='{cls}' tabindex='0'>{safe_icon}{title}</span></{tag}>",
        unsafe_allow_html=True,
    )


def render_progress_circle(percent: int, *, size: int = 90, thickness: int = 10, color: str = "#64b5f6", key: str | None = None) -> None:
    """Render a circular progress indicator with centered percentage.
    
    Args:
        percent: Progress percentage (0-100)
        size: Chart size in pixels
        thickness: Ring thickness in pixels  
        color: Color for the progress arc
    """
    # Create donut chart with two slices
    fig = go.Figure(data=[
        go.Pie(
            values=[percent, 100 - percent],
            hole=.7,  # Large hole for donut effect
            marker=dict(
                colors=[color, "#f0f0f0"],  # Progress color and background
                line=dict(width=0)  # No border
            ),
            textinfo='none',  # No text on slices
            hoverinfo='skip',  # No hover tooltips
            showlegend=False,
            direction='clockwise',
            sort=False
        )
    ])
    
    # Add percentage text in center
    fig.add_annotation(
        text=f"{percent}%",
        x=0.5,
        y=0.5,
        font_size=16,
        font_color="#333333",
        font_weight="bold",
        showarrow=False,
        xref="paper",
        yref="paper"
    )
    
    # Configure layout for compact size
    fig.update_layout(
        width=size,
        height=size,
        margin=dict(l=0, r=0, t=0, b=0),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )
    
    st.plotly_chart(fig, use_container_width=False, config={'displayModeBar': False}, key=key or f"prog-{percent}-{size}-{thickness}")
