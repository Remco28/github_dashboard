import streamlit as st
from typing import Dict, List
from services.next_steps import TaskItem, NextStepsDoc, summarize_tasks
from ui.components import render_progress_circle


def render_aggregate(tasks_by_repo: Dict[str, List[TaskItem]]) -> None:
    """
    Render aggregate NEXT_STEPS tasks summary across all repositories.
    
    Args:
        tasks_by_repo: Dictionary mapping repo full names to lists of TaskItem
    """
    if not tasks_by_repo:
        st.info("📝 No NEXT_STEPS.md files found in repositories.")
        st.markdown(
            "💡 Add NEXT_STEPS.md files to your repositories to track project tasks and milestones. "
            "See the template in this repo: [NEXT_STEPS.template.md](NEXT_STEPS.template.md)."
        )
        return
    
    # Calculate totals
    all_tasks = []
    for tasks in tasks_by_repo.values():
        all_tasks.extend(tasks)
    
    total_open, total_done = summarize_tasks(all_tasks)
    total_tasks = total_open + total_done
    
    # Display aggregate metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Tasks",
            total_tasks,
            help="Total number of tasks across all repositories"
        )
    
    with col2:
        st.metric(
            "Open Tasks",
            total_open,
            help="Number of incomplete tasks"
        )
    
    with col3:
        st.metric(
            "Completed Tasks",
            total_done,
            help="Number of completed tasks"
        )
    
    with col4:
        completion_rate = int((total_done / total_tasks * 100)) if total_tasks > 0 else 0
        st.metric(
            "Progress",
            f"{completion_rate}%",
            help="Overall completion rate"
        )
    
    # Display per-repository progress as compact grid (2 columns; 1 on mobile)
    st.subheader("Repository Progress")

    repo_items = []
    for repo_name, tasks in tasks_by_repo.items():
        repo_open, repo_done = summarize_tasks(tasks)
        repo_total = repo_open + repo_done
        if repo_total == 0:
            continue
        progress = repo_done / repo_total if repo_total > 0 else 0
        repo_items.append((repo_name, repo_done, repo_total, int(progress * 100)))

    if repo_items:
        cols = st.columns(3)
        for i, (repo_name, repo_done, repo_total, pct) in enumerate(repo_items):
            with cols[i % 3]:
                st.markdown(f"**{repo_name}**")
                render_progress_circle(pct, size=72, key=f"repo-progress-{repo_name}")
                st.caption(f"{repo_done}/{repo_total}")


def render_repo_next_steps(doc: NextStepsDoc) -> None:
    """
    Render a single repository's NEXT_STEPS.md as an interactive checklist.
    
    Args:
        doc: NextStepsDoc containing parsed tasks and sections
    """
    if not doc.raw_markdown:
        st.warning(f"No NEXT_STEPS.md found for {doc.repo_full_name}")
        st.info(
            "💡 Add a NEXT_STEPS.md file to this repository to track tasks and milestones. "
            "Use the template in this repo: [NEXT_STEPS.template.md](NEXT_STEPS.template.md)."
        )
        return
    
    st.subheader(f"📝 {doc.repo_full_name}")
    
    if not doc.tasks:
        st.info("This NEXT_STEPS.md file doesn't contain any checkable tasks.")
        with st.expander("View raw content"):
            st.markdown(doc.raw_markdown)
        return
    
    # Summary stats
    open_count, done_count = summarize_tasks(doc.tasks)
    total_tasks = open_count + done_count
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Tasks", total_tasks)
    with col2:
        st.metric("Open", open_count)
    with col3:
        st.metric("Completed", done_count)
    
    if total_tasks > 0:
        progress = done_count / total_tasks
        st.write(f"**Overall Progress: {done_count}/{total_tasks} tasks complete**")
        render_progress_circle(int(progress * 100), size=80, key=f"repo-overall-progress-{doc.repo_full_name}")
    
    # Group tasks by section
    tasks_by_section = {}
    for task in doc.tasks:
        section = task.section or "General"
        if section not in tasks_by_section:
            tasks_by_section[section] = []
        tasks_by_section[section].append(task)
    
    # Render tasks by section
    for section, section_tasks in tasks_by_section.items():
        if len(tasks_by_section) > 1:  # Only show section headers if multiple sections
            st.markdown(f"### {section}")
        
        for i, task in enumerate(section_tasks):
            # Use disabled checkbox to show status (read-only for MVP)
            key = f"task_{doc.repo_full_name}_{section}_{i}"
            st.checkbox(
                task.text,
                value=task.checked,
                disabled=True,
                key=key,
                help="Read-only view of task status"
            )


def render_missing_next_steps_guidance(repo_count: int) -> None:
    """
    Render guidance for repositories without NEXT_STEPS.md files.
    
    Args:
        repo_count: Number of repositories without NEXT_STEPS.md files
    """
    if repo_count == 0:
        return
    
    st.info(
        f"📝 {repo_count} repositories don't have NEXT_STEPS.md files. "
        "Add these files to track project tasks and milestones!"
    )
    
    with st.expander("📄 NEXT_STEPS.md Template"):
        st.markdown("""
        Create a `NEXT_STEPS.md` file in your repository root with content like:

        ```markdown
        # Next Steps for [Project Name]

        ## Immediate Tasks
        - [ ] Fix authentication bug in login flow
        - [x] Update dependencies to latest versions
        - [ ] Add unit tests for user service

        ## Future Enhancements
        - [ ] Add email notification system
        - [ ] Optimize database queries
        - [ ] Support extended activity window (e.g., 730 days)

        ## Documentation
        - [x] Write API documentation
        - [ ] Create user guide
        - [ ] Update deployment instructions
        ```

        Tasks with `- [ ]` are open, and `- [x]` are completed.
        """)
