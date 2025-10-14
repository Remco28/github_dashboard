from __future__ import annotations

import html
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, List, Optional, Sequence

import streamlit as st


@dataclass
class ActivityEntry:
    timestamp: str
    repo_name: str
    repo_url: str
    type_label: str
    type_url: str
    message: str


_STYLES_INJECTED_KEY = "gd_activity_feed_styles_v1"
_EVENT_CLASS_MAP = {
    "commit": "gd-activity-feed__event--commit",
    "merge": "gd-activity-feed__event--merge",
    "release": "gd-activity-feed__event--release",
    "branch": "gd-activity-feed__event--branch",
    "delete": "gd-activity-feed__event--delete",
    "star": "gd-activity-feed__event--star",
    "member": "gd-activity-feed__event--member",
}
_ACTIVITY_FEED_STYLES = """
<style>
.gd-activity-feed-divider {
    border: none;
    border-top: 1px solid #d1d5db;
    margin: 0.75rem 0;
}

.gd-activity-feed {
    background: transparent;
    border-radius: 0;
    font-family: "Fira Code", "JetBrains Mono", "SFMono-Regular", SFMono, Menlo, Monaco, Consolas, "Liberation Mono", "Courier New", monospace;
    font-size: 0.9rem;
    line-height: 1.6;
    max-height: 400px;
    overflow-y: auto;
    padding: 0.25rem 0;
    border: none;
}

.gd-activity-feed__item {
    color: #1f2933;
    white-space: nowrap;
    overflow: hidden;
    text-overflow: ellipsis;
}

.gd-activity-feed__timestamp {
    color: #6b7280;
}

.gd-activity-feed__repo {
    color: #2864dc;
    font-weight: 600;
}

.gd-activity-feed__repo a {
    color: inherit;
    text-decoration: none;
}

.gd-activity-feed__event {
    font-weight: 600;
}

.gd-activity-feed__event a {
    color: inherit;
    text-decoration: none;
}

.gd-activity-feed__event--commit { color: #047857; }
.gd-activity-feed__event--merge { color: #0f766e; }
.gd-activity-feed__event--release { color: #7c3aed; }
.gd-activity-feed__event--branch { color: #0ea5e9; }
.gd-activity-feed__event--delete { color: #b91c1c; }
.gd-activity-feed__event--star { color: #b45309; }
.gd-activity-feed__event--member { color: #6d28d9; }

.gd-activity-feed__message {
    color: #111827;
}

.gd-activity-feed__item a {
    color: inherit;
    text-decoration: none;
}

.gd-activity-feed__item a:hover,
.gd-activity-feed__item a:focus {
    text-decoration: none;
}

.gd-activity-feed__empty {
    color: #4b5563;
    font-style: italic;
}
</style>
"""


def render_activity_feed(events: Sequence[dict], *, current_username: Optional[str] = None) -> None:
    """Render the Recent Activity feed in a console-log style view."""
    _inject_styles_once()

    st.markdown('<hr class="gd-activity-feed-divider" />', unsafe_allow_html=True)

    container = st.container()
    container.markdown('<div class="gd-activity-feed">', unsafe_allow_html=True)

    entries = _build_activity_entries(events, current_username=current_username)

    if not entries:
        container.markdown('<div class="gd-activity-feed__empty">No recent activity to display.</div>', unsafe_allow_html=True)
    else:
        for entry in entries:
            container.markdown(_build_entry_html(entry), unsafe_allow_html=True)

    container.markdown('</div>', unsafe_allow_html=True)


def _inject_styles_once() -> None:
    """Inject component styles only once per session."""
    if st.session_state.get(_STYLES_INJECTED_KEY):
        return

    st.markdown(_ACTIVITY_FEED_STYLES, unsafe_allow_html=True)
    st.session_state[_STYLES_INJECTED_KEY] = True


def _build_activity_entries(events: Sequence[dict], *, current_username: Optional[str], limit: int = 20) -> List[ActivityEntry]:
    """Transform raw GitHub events into feed entries."""
    handlers: dict[str, Callable[[dict, Optional[str]], Optional[ActivityEntry]]] = {
        "PushEvent": _handle_push_event,
        "PullRequestEvent": _handle_pull_request_event,
        "ReleaseEvent": _handle_release_event,
        "CreateEvent": _handle_create_event,
        "DeleteEvent": _handle_delete_event,
        "WatchEvent": _handle_watch_event,
        "MemberEvent": _handle_member_event,
    }

    entries: List[ActivityEntry] = []
    for event in events:
        if len(entries) >= limit:
            break

        event_type = event.get("type")
        handler = handlers.get(event_type)
        if not handler:
            continue

        entry = handler(event, current_username)
        if entry:
            entries.append(entry)

    return entries


def _handle_push_event(event: dict, current_username: Optional[str]) -> Optional[ActivityEntry]:
    repo_slug = _repo_name(event)
    commits = (event.get("payload") or {}).get("commits") or []
    if not repo_slug or not commits:
        return None

    latest_commit = commits[-1]
    sha = latest_commit.get("sha")
    if not sha:
        return None

    message = latest_commit.get("message") or "Commit pushed"
    message = _normalize_message(message)

    commit_url = f"https://github.com/{repo_slug}/commit/{sha}"
    return ActivityEntry(
        timestamp=_format_timestamp(event.get("created_at")),
        repo_name=_format_repo_label(repo_slug, current_username),
        repo_url=_repo_html_url(repo_slug),
        type_label="Commit",
        type_url=commit_url,
        message=message,
    )


def _handle_pull_request_event(event: dict, current_username: Optional[str]) -> Optional[ActivityEntry]:
    payload = event.get("payload") or {}
    if payload.get("action") != "closed":
        return None

    pull_request = payload.get("pull_request") or {}
    if not pull_request.get("merged"):
        return None

    repo_slug = _repo_name(event)
    if not repo_slug:
        return None

    title = pull_request.get("title") or "Pull request merged"
    return ActivityEntry(
        timestamp=_format_timestamp(event.get("created_at")),
        repo_name=_format_repo_label(repo_slug, current_username),
        repo_url=_repo_html_url(repo_slug),
        type_label="Merge",
        type_url=pull_request.get("html_url") or _repo_html_url(repo_slug),
        message=_normalize_message(title),
    )


def _handle_release_event(event: dict, current_username: Optional[str]) -> Optional[ActivityEntry]:
    repo_slug = _repo_name(event)
    release = (event.get("payload") or {}).get("release") or {}
    if not repo_slug or not release:
        return None

    title = release.get("name") or release.get("tag_name") or "Release published"
    return ActivityEntry(
        timestamp=_format_timestamp(event.get("created_at")),
        repo_name=_format_repo_label(repo_slug, current_username),
        repo_url=_repo_html_url(repo_slug),
        type_label="Release",
        type_url=release.get("html_url") or _repo_html_url(repo_slug),
        message=_normalize_message(title),
    )


def _handle_create_event(event: dict, current_username: Optional[str]) -> Optional[ActivityEntry]:
    repo_slug = _repo_name(event)
    payload = event.get("payload") or {}
    ref_type = payload.get("ref_type")
    ref = payload.get("ref")
    if not repo_slug or not ref_type or not ref:
        return None

    if ref_type != "branch":
        return None

    message = f'Created branch: {ref}'
    type_url = f"https://github.com/{repo_slug}/tree/{ref}"

    return ActivityEntry(
        timestamp=_format_timestamp(event.get("created_at")),
        repo_name=_format_repo_label(repo_slug, current_username),
        repo_url=_repo_html_url(repo_slug),
        type_label="Branch",
        type_url=type_url,
        message=_normalize_message(message),
    )


def _handle_delete_event(event: dict, current_username: Optional[str]) -> Optional[ActivityEntry]:
    repo_slug = _repo_name(event)
    payload = event.get("payload") or {}
    ref_type = payload.get("ref_type")
    ref = payload.get("ref")
    if not repo_slug or not ref_type or not ref:
        return None

    if ref_type != "branch":
        return None

    message = f'Deleted {ref_type}: {ref}'
    return ActivityEntry(
        timestamp=_format_timestamp(event.get("created_at")),
        repo_name=_format_repo_label(repo_slug, current_username),
        repo_url=_repo_html_url(repo_slug),
        type_label="Delete",
        type_url=_repo_html_url(repo_slug),
        message=_normalize_message(message),
    )


def _handle_watch_event(event: dict, current_username: Optional[str]) -> Optional[ActivityEntry]:
    repo_slug = _repo_name(event)
    if not repo_slug:
        return None

    return ActivityEntry(
        timestamp=_format_timestamp(event.get("created_at")),
        repo_name=_format_repo_label(repo_slug, current_username),
        repo_url=_repo_html_url(repo_slug),
        type_label="Star",
        type_url=f"https://github.com/{repo_slug}/stargazers",
        message="Starred repository",
    )


def _handle_member_event(event: dict, current_username: Optional[str]) -> Optional[ActivityEntry]:
    repo_slug = _repo_name(event)
    payload = event.get("payload") or {}
    member = (payload.get("member") or {}).get("login")
    action = payload.get("action")
    if not repo_slug or not member or not action:
        return None

    action_text = {
        "added": "Added collaborator",
        "removed": "Removed collaborator",
        "edited": "Updated collaborator",
    }.get(action, "Updated collaborator")

    message = f'{action_text}: @{member}'

    return ActivityEntry(
        timestamp=_format_timestamp(event.get("created_at")),
        repo_name=_format_repo_label(repo_slug, current_username),
        repo_url=_repo_html_url(repo_slug),
        type_label="Member",
        type_url=_repo_html_url(repo_slug),
        message=_normalize_message(message),
    )


def _build_entry_html(entry: ActivityEntry) -> str:
    """Build HTML string for a single activity entry."""
    repo_html = html.escape(entry.repo_name)
    type_html = html.escape(entry.type_label)
    message_html = html.escape(entry.message, quote=False)

    event_classes = ["gd-activity-feed__event"]
    mapped = _EVENT_CLASS_MAP.get(entry.type_label.lower())
    if mapped:
        event_classes.append(mapped)
    event_class_attr = " ".join(event_classes)

    timestamp_html = f'<span class="gd-activity-feed__timestamp">[{entry.timestamp}]</span>'
    repo_link_html = (
        f'<span class="gd-activity-feed__repo">'
        f'[<a href="{entry.repo_url}" target="_blank" rel="noopener noreferrer">{repo_html}</a>]'
        "</span>"
    )
    event_link_html = (
        f'<span class="{event_class_attr}">'
        f'[<a href="{entry.type_url}" target="_blank" rel="noopener noreferrer">{type_html}</a>]'
        "</span>"
    )
    message_span_html = f'<span class="gd-activity-feed__message"> "{message_html}"</span>'

    return (
        '<div class="gd-activity-feed__item">'
        f'{timestamp_html}{repo_link_html}{event_link_html}{message_span_html}'
        "</div>"
    )


def _format_timestamp(raw: Optional[str]) -> str:
    if not raw:
        return "--"

    try:
        dt = datetime.fromisoformat(raw.replace("Z", "+00:00"))
        dt = dt.astimezone(timezone.utc)
    except ValueError:
        return raw

    return dt.strftime("%Y-%m-%d %H:%M")


def _repo_name(event: dict) -> Optional[str]:
    repo = event.get("repo") or {}
    return repo.get("name")


def _repo_html_url(repo_name: str) -> str:
    return f"https://github.com/{repo_name}"


def _format_repo_label(repo_slug: str, current_username: Optional[str]) -> str:
    if not current_username:
        return repo_slug

    owner, _, repo = repo_slug.partition("/")
    if owner.lower() == current_username.lower() and repo:
        return repo

    return repo_slug


def _normalize_message(message: str) -> str:
    """Ensure activity messages render as a single clean line."""
    cleaned = " ".join(message.strip().splitlines())
    return cleaned[:240] if len(cleaned) > 240 else cleaned
