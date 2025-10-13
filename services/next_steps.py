import re
import base64
from dataclasses import dataclass
from typing import List
from services.github_client import get_file_contents


@dataclass
class TaskItem:
    """A single task item from NEXT_STEPS.md"""
    text: str
    checked: bool
    section: str | None = None


@dataclass
class NextStepsDoc:
    """Parsed NEXT_STEPS.md document for a repository"""
    repo_full_name: str
    raw_markdown: str | None
    tasks: List[TaskItem]
    sections: List[str]


def fetch_next_steps(owner: str, repo: str, token: str) -> str | None:
    """
    Fetch NEXT_STEPS.md file content from a repository.

    Attempts to load comms/NEXT_STEPS.md first and falls back to the root
    NEXT_STEPS.md for backward compatibility.

    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub token

    Returns:
        Markdown content as string if file exists, None if not found
    """
    # Preferred location: comms/NEXT_STEPS.md
    file_data = get_file_contents(owner, repo, "comms/NEXT_STEPS.md", token)

    # Backward-compatible fallback to root
    if file_data is None:
        file_data = get_file_contents(owner, repo, "NEXT_STEPS.md", token)

    if file_data is None:
        return None

    # Decode base64 content to UTF-8 string
    content_b64 = file_data.get("content", "")
    if not content_b64:
        return None

    try:
        content_bytes = base64.b64decode(content_b64)
        return content_bytes.decode("utf-8")
    except (base64.binascii.Error, UnicodeDecodeError):
        return None


def parse_next_steps(md: str, repo_full_name: str) -> NextStepsDoc:
    """
    Parse NEXT_STEPS.md markdown content into structured data.
    
    Args:
        md: Markdown content string
        repo_full_name: Full repository name (owner/repo)
        
    Returns:
        NextStepsDoc with parsed tasks and sections
    """
    tasks = []
    sections = []
    current_section = None
    
    for line in md.splitlines():
        # Check for section headings (H1-H3)
        section_match = re.match(r"^(#{1,3})\s+(.*)$", line.strip())
        if section_match:
            current_section = section_match.group(2).strip()
            sections.append(current_section)
            continue
        
        # Check for checkbox items
        checkbox_match = re.match(r"^\s*[-*]\s+\[( |x|X)\]\s+(.*)$", line)
        if checkbox_match:
            checked = checkbox_match.group(1).lower() == 'x'
            text = checkbox_match.group(2).strip()
            tasks.append(TaskItem(
                text=text,
                checked=checked,
                section=current_section
            ))
    
    return NextStepsDoc(
        repo_full_name=repo_full_name,
        raw_markdown=md,
        tasks=tasks,
        sections=sections
    )


def summarize_tasks(tasks: List[TaskItem]) -> tuple[int, int]:
    """
    Summarize task completion status.
    
    Args:
        tasks: List of TaskItem objects
        
    Returns:
        Tuple of (open_count, done_count)
    """
    open_count = sum(1 for task in tasks if not task.checked)
    done_count = sum(1 for task in tasks if task.checked)
    return open_count, done_count
