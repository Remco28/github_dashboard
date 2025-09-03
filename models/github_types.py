from dataclasses import dataclass


@dataclass
class RepoSummary:
    name: str
    full_name: str
    private: bool
    stargazers_count: int
    forks_count: int
    open_issues_count: int
    pushed_at: str
    language: str | None
    html_url: str
    archived: bool
    disabled: bool
    default_branch: str