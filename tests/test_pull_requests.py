import pytest

from models.github_types import RepoSummary
from services.analytics import attach_pull_request_metadata
from services.errors import RateLimitError


def _make_repo(name: str = "alpha", full_name: str = "user/alpha") -> RepoSummary:
    return RepoSummary(
        name=name,
        full_name=full_name,
        private=False,
        stargazers_count=0,
        forks_count=0,
        open_issues_count=0,
        pushed_at="2025-10-10T00:00:00Z",
        language="Python",
        html_url=f"https://github.com/{full_name}",
        archived=False,
        disabled=False,
        default_branch="main",
    )


def test_attach_pull_request_metadata_counts_and_links(mocker):
    repo = _make_repo()
    mocker.patch(
        "services.cache.cached_list_repo_pull_requests",
        return_value=[
            {
                "html_url": "https://github.com/user/alpha/pull/10",
                "title": "Ready for review",
                "draft": False,
                "requested_reviewers": [{"login": "octocat"}],
                "requested_teams": [],
            },
            {
                "html_url": "https://github.com/user/alpha/pull/11",
                "title": "Draft work",
                "draft": True,
                "requested_reviewers": [{"login": "octocat"}],
                "requested_teams": [],
            },
            {
                "html_url": "https://github.com/user/alpha/pull/12",
                "title": "Small tweak",
                "draft": False,
                "requested_reviewers": [{"login": "someone-else"}],
                "requested_teams": [],
            },
        ],
    )

    result = attach_pull_request_metadata([repo], token="token", username="octocat")

    assert result[0].open_pr_count == 2  # Draft excluded
    assert result[0].needs_review_pr_count == 1
    assert result[0].needs_review_urls == ("https://github.com/user/alpha/pull/10",)


def test_attach_pull_request_metadata_matches_username_case_insensitively(mocker):
    repo = _make_repo()
    mocker.patch(
        "services.cache.cached_list_repo_pull_requests",
        return_value=[
            {
                "html_url": "https://github.com/user/alpha/pull/99",
                "title": "Hotfix",
                "draft": False,
                "requested_reviewers": [{"login": "OCTOCAT"}],
                "requested_teams": [],
            }
        ],
    )

    attach_pull_request_metadata([repo], token="token", username="octocat")

    assert repo.needs_review_pr_count == 1
    assert repo.needs_review_urls == ("https://github.com/user/alpha/pull/99",)


def test_attach_pull_request_metadata_rate_limit_propagates_and_leaves_defaults(mocker):
    repo = _make_repo()
    mocker.patch(
        "services.cache.cached_list_repo_pull_requests",
        side_effect=RateLimitError(403, "Rate limit exceeded"),
    )

    with pytest.raises(RateLimitError):
        attach_pull_request_metadata([repo], token="token", username="octocat")

    assert repo.open_pr_count == 0
    assert repo.needs_review_pr_count == 0
    assert repo.needs_review_urls == ()
