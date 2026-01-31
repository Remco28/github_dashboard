import streamlit as st
from typing import Dict, List
from services.features import FeatureItem, FeaturesDoc, summarize_features
from ui.metrics import render_progress_circle


def render_aggregate(features_by_repo: Dict[str, List[FeatureItem]]) -> None:
    """
    Render aggregate features summary across all repositories.

    Args:
        features_by_repo: Dictionary mapping repo full names to lists of FeatureItem
    """
    if not features_by_repo:
        st.info("No FEATURES.md files found in repositories.")
        st.markdown(
            "Add a `comms/FEATURES.md` file to your repositories to track product features."
        )
        return

    # Calculate totals
    all_features = []
    for features in features_by_repo.values():
        all_features.extend(features)

    not_delivered, delivered = summarize_features(all_features)
    total_features = not_delivered + delivered

    # Display aggregate metrics
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            "Total Features",
            total_features,
            help="Total number of features across all repositories"
        )

    with col2:
        st.metric(
            "Not Delivered",
            not_delivered,
            help="Number of features not yet delivered"
        )

    with col3:
        st.metric(
            "Delivered",
            delivered,
            help="Number of delivered features"
        )

    with col4:
        completion_rate = int((delivered / total_features * 100)) if total_features > 0 else 0
        st.metric(
            "Progress",
            f"{completion_rate}%",
            help="Overall feature delivery rate"
        )

    # Display per-repository progress as compact grid
    st.subheader("Feature Progress")

    repo_items = []
    for repo_name, features in features_by_repo.items():
        not_delivered_count, delivered_count = summarize_features(features)
        repo_total = not_delivered_count + delivered_count
        if repo_total == 0:
            continue
        progress = delivered_count / repo_total if repo_total > 0 else 0
        repo_items.append((repo_name, delivered_count, repo_total, int(progress * 100)))

    if repo_items:
        cols = st.columns(3)
        for i, (repo_name, repo_delivered, repo_total, pct) in enumerate(repo_items):
            with cols[i % 3]:
                # Truncate long repository names to prevent wrapping
                display_name = repo_name if len(repo_name) <= 30 else repo_name[:27] + "..."
                st.markdown(f"<div style='text-align: center; margin-bottom: 8px;'><strong title='{repo_name}'>{display_name}</strong></div>", unsafe_allow_html=True)
                render_progress_circle(pct, size=72, key=f"repo-progress-{repo_name}")
                st.markdown(f"<div style='text-align: center; margin-top: 4px; font-size: 12px; color: #666;'>{repo_delivered}/{repo_total}</div>", unsafe_allow_html=True)


def render_repo_features(doc: FeaturesDoc) -> None:
    """
    Render a single repository's FEATURES.md as a read-only checklist.

    Args:
        doc: FeaturesDoc containing parsed features and sections
    """
    if not doc.raw_markdown:
        st.warning(f"No FEATURES.md found for {doc.repo_full_name}")
        st.info(
            "Add a `comms/FEATURES.md` file to this repository to track product features."
        )
        return

    st.subheader(f"{doc.repo_full_name}")

    if not doc.features:
        st.info("This FEATURES.md file doesn't contain any checkable items.")
        with st.expander("View raw content"):
            st.markdown(doc.raw_markdown)
        return

    # Summary stats
    not_delivered, delivered = summarize_features(doc.features)
    total_features = not_delivered + delivered

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Features", total_features)
    with col2:
        st.metric("Not Delivered", not_delivered)
    with col3:
        st.metric("Delivered", delivered)

    if total_features > 0:
        progress = delivered / total_features
        st.write(f"**Overall Progress: {delivered}/{total_features} features delivered**")
        render_progress_circle(int(progress * 100), size=80, key=f"repo-overall-progress-{doc.repo_full_name}")

    # Group features by section
    features_by_section = {}
    for feature in doc.features:
        section = feature.section or "General"
        if section not in features_by_section:
            features_by_section[section] = []
        features_by_section[section].append(feature)

    # Render features by section
    for section, section_features in features_by_section.items():
        if len(features_by_section) > 1:  # Only show section headers if multiple sections
            st.markdown(f"### {section}")

        for i, feature in enumerate(section_features):
            # Use disabled checkbox to show status (read-only)
            key = f"feature_{doc.repo_full_name}_{section}_{i}"
            st.checkbox(
                feature.text,
                value=feature.delivered,
                disabled=True,
                key=key,
                help="Read-only view of feature status"
            )


def render_missing_features_guidance(repo_count: int) -> None:
    """
    Render guidance for repositories without FEATURES.md files.

    Args:
        repo_count: Number of repositories without FEATURES.md files
    """
    if repo_count == 0:
        return

    st.info(
        f"{repo_count} repositories don't have FEATURES.md files. "
        "Add these files to track product features!"
    )

    with st.expander("FEATURES.md Template"):
        st.markdown("""
        Create a `comms/FEATURES.md` file in your repository with content like:

        ```markdown
        # My App

        A brief description of your application.

        ## Features
        - [x] User authentication and login
        - [x] Dashboard with key metrics
        - [ ] Export data to CSV
        - [ ] Email notifications

        ## Data
        - [x] Real-time data sync
        - [ ] Offline mode support
        ```

        Features with `- [x]` are delivered, and `- [ ]` are not yet delivered.
        """)
