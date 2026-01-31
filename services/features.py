import re
import base64
from dataclasses import dataclass
from typing import List
from services.github_client import get_file_contents


@dataclass
class FeatureItem:
    """A single feature item from FEATURES.md"""
    text: str
    delivered: bool
    section: str | None = None


@dataclass
class FeaturesDoc:
    """Parsed FEATURES.md document for a repository"""
    repo_full_name: str
    raw_markdown: str | None
    features: List[FeatureItem]
    sections: List[str]


def fetch_features(owner: str, repo: str, token: str) -> str | None:
    """
    Fetch FEATURES.md file content from a repository.

    Loads comms/FEATURES.md only (no fallback to root).

    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub token

    Returns:
        Markdown content as string if file exists, None if not found
    """
    file_data = get_file_contents(owner, repo, "comms/FEATURES.md", token)

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


def parse_features(md: str, repo_full_name: str) -> FeaturesDoc:
    """
    Parse FEATURES.md markdown content into structured data.

    Args:
        md: Markdown content string
        repo_full_name: Full repository name (owner/repo)

    Returns:
        FeaturesDoc with parsed features and sections
    """
    features = []
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
            delivered = checkbox_match.group(1).lower() == 'x'
            text = checkbox_match.group(2).strip()
            features.append(FeatureItem(
                text=text,
                delivered=delivered,
                section=current_section
            ))

    return FeaturesDoc(
        repo_full_name=repo_full_name,
        raw_markdown=md,
        features=features,
        sections=sections
    )


def summarize_features(features: List[FeatureItem]) -> tuple[int, int]:
    """
    Summarize feature delivery status.

    Args:
        features: List of FeatureItem objects

    Returns:
        Tuple of (not_delivered_count, delivered_count)
    """
    not_delivered = sum(1 for f in features if not f.delivered)
    delivered = sum(1 for f in features if f.delivered)
    return not_delivered, delivered
