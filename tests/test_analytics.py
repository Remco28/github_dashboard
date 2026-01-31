from datetime import datetime, timedelta, timezone
from typing import List

import pytest

from models.github_types import RepoSummary
from services import analytics


@pytest.fixture
def sample_repos() -> List[RepoSummary]:
    """Fixture providing representative repository summaries."""
    now = datetime.now(timezone.utc)
    fresh = (now - timedelta(days=1)).isoformat().replace("+00:00", "Z")
    recent = (now - timedelta(days=5)).isoformat().replace("+00:00", "Z")
    stale = (now - timedelta(days=30)).isoformat().replace("+00:00", "Z")

    return [
        RepoSummary(
            name="alpha",
            full_name="user/alpha",
            private=False,
            open_issues_count=1,
            pushed_at=fresh,
            language="Python",
            html_url="https://github.com/user/alpha",
            archived=False,
            disabled=False,
            default_branch="main",
        ),
        RepoSummary(
            name="beta",
            full_name="user/beta",
            private=True,
            open_issues_count=0,
            pushed_at=stale,
            language="JavaScript",
            html_url="https://github.com/user/beta",
            archived=False,
            disabled=False,
            default_branch="main",
        ),
        RepoSummary(
            name="gamma",
            full_name="user/gamma",
            private=False,
            open_issues_count=0,
            pushed_at=None,
            language=None,
            html_url="https://github.com/user/gamma",
            archived=False,
            disabled=False,
            default_branch="main",
        ),
        RepoSummary(
            name="delta",
            full_name="user/delta",
            private=True,
            open_issues_count=2,
            pushed_at=recent,
            language="Python",
            html_url="https://github.com/user/delta",
            archived=False,
            disabled=False,
            default_branch="main",
        ),
    ]


def test_filter_repos_by_language_returns_matching_repos(sample_repos):
    result = analytics.filter_repos(sample_repos, languages={"Python"})

    assert [repo.name for repo in result] == ["alpha", "delta"]


def test_filter_repos_by_visibility_excludes_private_when_requested(sample_repos):
    result = analytics.filter_repos(sample_repos, include_private=False)

    assert all(not repo.private for repo in result)
    assert {repo.name for repo in result} == {"alpha", "gamma"}


def test_filter_repos_activity_window_filters_out_stale_repos(sample_repos):
    result = analytics.filter_repos(sample_repos, activity_days=10)

    assert {repo.name for repo in result} == {"alpha", "gamma", "delta"}


def test_filter_repos_query_matches_case_insensitively(sample_repos):
    result = analytics.filter_repos(sample_repos, query="DEL")

    assert len(result) == 1
    assert result[0].name == "delta"


def test_filter_repos_combined_filters(sample_repos):
    result = analytics.filter_repos(
        sample_repos,
        languages={"Python"},
        include_private=True,
        activity_days=9,
        query="del",
    )

    assert len(result) == 1
    assert result[0].name == "delta"


def test_language_distribution_counts_languages(sample_repos):
    result = analytics.language_distribution(sample_repos)

    assert result == {"Python": 2, "JavaScript": 1}


def test_language_distribution_handles_empty_list():
    assert analytics.language_distribution([]) == {}


def test_language_distribution_ignores_missing_language(sample_repos):
    # Remove language values to ensure they are ignored
    repos = [repo for repo in sample_repos]
    repos[0].language = None
    repos[1].language = ""

    result = analytics.language_distribution(repos)

    assert result == {"Python": 1}


def test_commits_per_repo_counts_commits_and_sorts(sample_repos, mocker):
    mock_cached_commits = mocker.patch(
        "services.cache.cached_list_repo_commits",
        side_effect=[
            [{"sha": "1"}, {"sha": "2"}, {"sha": "3"}],
            [],
            [{"sha": "a"}],
        ],
    )

    result = analytics.commits_per_repo(
        sample_repos,
        token="token",
        since="2025-09-01T00:00:00Z",
        until="2025-10-13T00:00:00Z",
        max_repos=3,
    )

    assert result == [("alpha", 3), ("gamma", 1), ("beta", 0)]
    assert mock_cached_commits.call_count == 3


def test_commits_per_repo_handles_empty_commit_responses(sample_repos, mocker):
    mocker.patch(
        "services.cache.cached_list_repo_commits",
        return_value=[],
    )

    result = analytics.commits_per_repo(
        sample_repos,
        token="token",
        since="2025-09-01T00:00:00Z",
        until="2025-10-13T00:00:00Z",
        max_repos=1,
    )

    assert result == [("alpha", 0)]


def test_commits_per_repo_respects_max_repos_limit(sample_repos, mocker):
    mock_cached = mocker.patch(
        "services.cache.cached_list_repo_commits",
        return_value=[{"sha": "1"}],
    )

    analytics.commits_per_repo(
        sample_repos,
        token="token",
        since="2025-09-01T00:00:00Z",
        until="2025-10-13T00:00:00Z",
        max_repos=2,
    )

    assert mock_cached.call_count == 2
