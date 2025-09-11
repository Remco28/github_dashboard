import base64
import streamlit as st


def get_logo_base64() -> str:
    """Load and encode the app logo image as base64.

    Relocated from ui.components to keep branding assets together.
    """
    try:
        with open("media/logo_trans_blue_med.png", "rb") as img_file:
            return base64.b64encode(img_file.read()).decode()
    except FileNotFoundError:
        return ""


def render_app_title() -> None:
    """Render the centered app title with logo.

    Pure relocation of the inline HTML previously in app.py.
    """
    logo_b64 = get_logo_base64()
    st.markdown(
        f"""
        <div style="text-align: center; margin-bottom: 2rem;">
            <h1 style="font-weight: 600; margin: 0 0 0.4rem 0;">
                <span style="font-size: 4rem; color: #566C81; font-family: 'JetBrains Mono', Consolas, Monaco, 'Lucida Console', monospace;">DASHBOARD</span>
                <span style="font-size: 2rem; font-style: italic; color: #566C81; margin-left: 0.5rem; font-family: 'Crimson Text', Cambria, 'Times New Roman', serif; position: relative; top: -1rem;">for GitHub</span>
            </h1>
            <img src="data:image/png;base64,{logo_b64}" style="height: 4rem; width: 4rem;">
        </div>
        """,
        unsafe_allow_html=True,
    )

