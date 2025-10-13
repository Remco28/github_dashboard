from dataclasses import dataclass, field


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
    open_pr_count: int = 0
    needs_review_pr_count: int = 0
    # Stores canonical PR URLs for hover/tooltip usage when review is needed.
    needs_review_urls: tuple[str, ...] = field(default_factory=tuple)
