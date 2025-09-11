import streamlit as st


def ensure_section_header_styles() -> None:
    """Inject section header styles with :has() hover effects.

    Relocated from ui.components to isolate header styling concerns.
    """
    st.markdown("""
    <style>
      @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&display=swap');
      
      .gd-section { margin: 0 0 8px; }
      
      /* Reduce spacing around horizontal rules */
      hr { margin: 8px 0 4px 0 !important; }
      
      .gd-section-title {
        display: inline-block; 
        font-family: 'Bebas Neue', system-ui, -apple-system, Segoe UI, Roboto, Ubuntu, Cantarell, Noto Sans, Helvetica, Arial, sans-serif;
        font-size: clamp(1.4rem, 3.5vw, 2.2rem);
        letter-spacing: 0.5px;
        color: #1f2937; 
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
        accent: Color accent ('gold', 'blue', 'green', 'red', 'purple')
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

