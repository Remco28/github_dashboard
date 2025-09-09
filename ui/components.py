import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from models.github_types import RepoSummary


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


def ensure_section_header_styles() -> None:
    """Inject section header styles only once per session."""
    if st.session_state.get('_gd_section_css_loaded'):
        return
        
    st.markdown("""
    <style>
      .gd-section { margin: 16px 0 8px; }
      .gd-section-title { 
        display: inline; 
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
      .gd-section-title:hover, .gd-section-title:focus-visible,
      .gd-section-wrap:hover .gd-section-title,
      .gd-section-wrap:focus-within .gd-section-title,
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
    <script>
    (function(){
      if (window._gdHeaderEnhancerLoaded) return; 
      window._gdHeaderEnhancerLoaded = true;
      
      const setupHeader = el => {
        try {
          // Find container - try multiple selectors in order
          let block = el.closest('div[data-testid="stVerticalBlock"]') || 
                      el.closest('div.block-container') || 
                      el.closest('section.main');
          
          // Fallback: walk up parent hierarchy
          if (!block) {
            let parent = el.parentElement;
            for (let i = 0; i < 5 && parent; i++) {
              if (parent.tagName === 'DIV' && parent.className) {
                block = parent;
                break;
              }
              parent = parent.parentElement;
            }
          }
          
          if (block && !block.classList.contains('gd-section-wrap')) {
            block.classList.add('gd-section-wrap');
            
            // Add mouse listeners for data attribute activation
            block.addEventListener('mouseenter', () => {
              el.setAttribute('data-gd-active', 'true');
            });
            
            block.addEventListener('mouseleave', () => {
              el.removeAttribute('data-gd-active');
            });

            // Keyboard focus within the section keeps highlight
            block.addEventListener('focusin', () => {
              el.setAttribute('data-gd-active', 'true');
            });
            block.addEventListener('focusout', (ev) => {
              // Only remove if focus left the block entirely
              if (!block.contains(ev.relatedTarget)) {
                el.removeAttribute('data-gd-active');
              }
            });
          }
        } catch(_) {}
      };
      
      const headers = () => Array.from(document.querySelectorAll('.gd-section-title'));
      const allBlocks = () => Array.from(document.querySelectorAll('div[data-testid="stVerticalBlock"]'));
      const getNearestBlock = (el) => el.closest('div[data-testid="stVerticalBlock"]') || el.closest('div.block-container') || el.closest('section.main');
      
      const bindRangeBlocks = () => {
        const hs = headers();
        const blocks = allBlocks();
        if (!hs.length || !blocks.length) return;
        
        // Build header info with block index
        const infos = hs.map((el, idx) => {
          const block = getNearestBlock(el);
          const bi = blocks.indexOf(block);
          el.dataset.gdId = String(idx);
          return { el, block, bi: bi < 0 ? 0 : bi };
        }).sort((a,b) => a.bi - b.bi);
        
        for (let i = 0; i < infos.length; i++) {
          const cur = infos[i];
          const next = infos[i+1];
          const end = next ? next.bi : blocks.length;
          for (let j = cur.bi; j < end; j++) {
            const b = blocks[j];
            if (!b) continue;
            if (!b.classList.contains('gd-section-wrap')) b.classList.add('gd-section-wrap');
            const key = `gdBoundFor-${cur.el.dataset.gdId}`;
            if (b.dataset[key]) continue; // skip if already bound for this header
            b.dataset[key] = '1';
            b.addEventListener('mouseenter', () => cur.el.setAttribute('data-gd-active', 'true'));
            b.addEventListener('mouseleave', () => cur.el.removeAttribute('data-gd-active'));
            b.addEventListener('focusin', () => cur.el.setAttribute('data-gd-active', 'true'));
            b.addEventListener('focusout', (ev) => { if (!b.contains(ev.relatedTarget)) cur.el.removeAttribute('data-gd-active'); });
          }
        }
      };
      const mo = new MutationObserver(scan); 
      mo.observe(document.body, {childList:true, subtree:true});
      document.addEventListener('DOMContentLoaded', () => { scan(); bindRangeBlocks(); }); 
      scan();
      bindRangeBlocks();
    })();
    </script>
    """, unsafe_allow_html=True)
    st.session_state['_gd_section_css_loaded'] = True


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
