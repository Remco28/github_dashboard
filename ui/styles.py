import streamlit as st


def inject_global_styles() -> None:
    """Inject global CSS styles used across the app.

    This function was moved from ui.components to keep concerns focused.
    """
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
    """Inject a small script to hide header Deploy controls in local dev.

    Moved from ui.components for cohesion with other style-related helpers.
    """
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
          } catch (e) { console.warn('deploy hider error', e); }
        });
        </script>
        """,
        unsafe_allow_html=True,
    )

