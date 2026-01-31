from datetime import datetime, timedelta, timezone
from typing import List, Set, Optional, Tuple, Dict
from collections import defaultdict
from models.github_types import RepoSummary


def filter_repos(
    repos: List[RepoSummary],
    languages: Optional[Set[str]] = None,
    include_private: Optional[bool] = None,
    activity_days: Optional[int] = None,
    query: Optional[str] = None
) -> List[RepoSummary]:
    """
    Apply filters to repository list.

    Args:
        repos: List of repository summaries to filter
        languages: Set of languages to include (None = include all)
        include_private: True for private only, False for public only, None for all
        activity_days: Number of days for recent activity filter (None = no filter)
        query: Search query for repository name (case-insensitive, None = no filter)

    Returns:
        Filtered list of repository summaries
    """
    filtered_repos = []
    # Use naive UTC for consistent comparisons
    now = datetime.now(timezone.utc).replace(tzinfo=None)

    for repo in repos:
        # Language filter
        if languages is not None:
            if not repo.language or repo.language not in languages:
                continue

        # Visibility filter
        if include_private is not None:
            if repo.private != include_private:
                continue

        # Activity filter
        if activity_days is not None and repo.pushed_at:
            try:
                # Handle ISO format with Z
                date_str = repo.pushed_at
                if date_str.endswith('Z'):
                    date_str = date_str[:-1] + '+00:00'

                # Parse the datetime
                if 'T' in date_str:
                    repo_date = datetime.fromisoformat(date_str)
                else:
                    # If it's just a date
                    repo_date = datetime.fromisoformat(date_str + 'T00:00:00+00:00')

                # Remove timezone info for comparison
                if repo_date.tzinfo:
                    repo_date = repo_date.replace(tzinfo=None)

                days_old = (now - repo_date).days
                if days_old > activity_days:
                    continue
            except (ValueError, AttributeError):
                # If we can't parse the date, skip this filter
                pass

        # Name search filter
        if query is not None:
            if query.lower() not in repo.name.lower():
                continue

        filtered_repos.append(repo)

    return filtered_repos


def languages_set(repos: List[RepoSummary]) -> List[str]:
    """
    Extract unique programming languages from repositories.

    Args:
        repos: List of repository summaries

    Returns:
        Sorted list of unique languages (excludes None/empty)
    """
    languages = set()

    for repo in repos:
        if repo.language:
            languages.add(repo.language)

    return sorted(list(languages))


def language_distribution(repos: List[RepoSummary]) -> Dict[str, int]:
    """
    Count repositories by programming language for pie chart.

    Args:
        repos: List of repository summaries

    Returns:
        Dictionary mapping language names to repository counts (excludes None/empty)
    """
    language_counts = defaultdict(int)

    for repo in repos:
        if repo.language:
            language_counts[repo.language] += 1

    return dict(language_counts)


def commits_per_repo(repos: List[RepoSummary], token: str, since: str, until: str, max_repos: int = 10, cache_bust: Optional[str] = None) -> List[Tuple[str, int]]:
    """
    Get commit counts per repository for the most recently pushed repositories.

    Args:
        repos: List of repository summaries (should be sorted by pushed_at desc)
        token: GitHub token
        since: ISO datetime string (start of window)
        until: ISO datetime string (end of window)
        max_repos: Maximum number of repositories to analyze
        cache_bust: Optional cache bust parameter

    Returns:
        List of (repo_name, commit_count) tuples sorted by commit count desc
    """
    from services.cache import cached_list_repo_commits

    # Take the most recently pushed repositories
    selected_repos = repos[:max_repos]
    repo_commit_counts = []

    for repo in selected_repos:
        try:
            # Extract owner and repo name from full_name
            owner, repo_name = repo.full_name.split('/', 1)

            # Fetch commits for this repository
            commits = cached_list_repo_commits(owner, repo_name, token, since, until, cache_bust)
            repo_commit_counts.append((repo.name, len(commits)))

        except Exception:
            # If we can't fetch commits for a repo, skip it or count as 0
            repo_commit_counts.append((repo.name, 0))

    # Sort by commit count descending
    return sorted(repo_commit_counts, key=lambda x: x[1], reverse=True)


def commits_over_time(repos: List[RepoSummary], token: str, since: str, until: str, max_repos: int = 10, freq: str = "W", cache_bust: Optional[str] = None) -> List[Tuple[str, int]]:
    """
    Aggregate commits over time into bins for trend visualization.

    Args:
        repos: List of repository summaries
        token: GitHub token
        since: ISO datetime string (start of window)
        until: ISO datetime string (end of window)
        max_repos: Maximum number of repositories to analyze
        freq: Frequency for binning ("W" for weekly, "D" for daily)
        cache_bust: Optional cache bust parameter

    Returns:
        List of (timestamp, total_commits) tuples sorted by time
    """
    from services.cache import cached_list_repo_commits

    selected_repos = repos[:max_repos]
    all_commits = []

    # Collect all commits from selected repositories
    for repo in selected_repos:
        try:
            owner, repo_name = repo.full_name.split('/', 1)
            commits = cached_list_repo_commits(owner, repo_name, token, since, until, cache_bust)
            all_commits.extend(commits)
        except Exception:
            continue

    # Group commits by time bins
    time_bins = defaultdict(int)

    for commit in all_commits:
        try:
            # Extract commit date
            commit_date_str = (
                commit.get('commit', {}).get('author', {}).get('date') or
                commit.get('commit', {}).get('committer', {}).get('date')
            )

            if commit_date_str:
                # Parse the date and bin it
                commit_date = datetime.fromisoformat(commit_date_str.replace('Z', '+00:00'))

                if freq == "W":
                    # Weekly binning - start of week
                    week_start = commit_date - timedelta(days=commit_date.weekday())
                    bin_key = week_start.strftime('%Y-%m-%d')
                else:
                    # Daily binning
                    bin_key = commit_date.strftime('%Y-%m-%d')

                time_bins[bin_key] += 1
        except Exception:
            continue

    # Convert to sorted list
    return sorted(time_bins.items(), key=lambda x: x[0])


def heatmap_counts(repos: List[RepoSummary], token: str, since: str, until: str, max_repos: int = 10, cache_bust: Optional[str] = None) -> Dict[str, int]:
    """
    Generate daily commit counts for heatmap visualization.

    Args:
        repos: List of repository summaries
        token: GitHub token
        since: ISO datetime string (start of window)
        until: ISO datetime string (end of window)
        max_repos: Maximum number of repositories to analyze
        cache_bust: Optional cache bust parameter

    Returns:
        Dictionary mapping YYYY-MM-DD dates to commit counts
    """
    from services.cache import cached_list_repo_commits

    selected_repos = repos[:max_repos]
    daily_counts = defaultdict(int)

    for repo in selected_repos:
        try:
            owner, repo_name = repo.full_name.split('/', 1)
            commits = cached_list_repo_commits(owner, repo_name, token, since, until, cache_bust)

            for commit in commits:
                try:
                    # Extract commit date
                    commit_date_str = (
                        commit.get('commit', {}).get('author', {}).get('date') or
                        commit.get('commit', {}).get('committer', {}).get('date')
                    )

                    if commit_date_str:
                        # Parse date and extract day
                        day = commit_date_str.split('T')[0]  # Get YYYY-MM-DD part
                        daily_counts[day] += 1
                except Exception:
                    continue
        except Exception:
            continue

    return dict(daily_counts)
