import streamlit as st

# Transitional re-exports for split modules (safe to remove later)
from ui.styles import inject_global_styles, inject_header_deploy_hider  # noqa: F401
from ui.branding import get_logo_base64  # noqa: F401
from ui.headers import ensure_section_header_styles, render_section_header  # noqa: F401
from ui.metrics import render_stat_cards, render_progress_circle  # noqa: F401
from ui.tables import render_repo_table  # noqa: F401


# render_stat_cards now lives in ui.metrics (re-exported above)


# render_repo_table now lives in ui.tables (re-exported above)




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


# render_progress_circle now lives in ui.metrics (re-exported above)
