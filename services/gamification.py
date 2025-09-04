from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
from models.github_types import RepoSummary


@dataclass
class StreakStats:
    """Statistics about activity streaks"""
    current: int
    longest: int
    last_active: str | None


@dataclass
class Badge:
    """A gamification badge with display information"""
    key: str
    label: str
    emoji: str
    description: str


def compute_activity_dates(commits_by_repo: Dict[str, List[Dict]]) -> set[str]:
    """
    Extract unique UTC dates (YYYY-MM-DD) from commit timestamps across repos.
    
    Args:
        commits_by_repo: Dictionary mapping repo names to lists of commit objects
        
    Returns:
        Set of unique date strings in YYYY-MM-DD format
    """
    activity_dates = set()
    
    for repo_commits in commits_by_repo.values():
        for commit in repo_commits:
            # Extract date from commit timestamp
            try:
                # Handle different timestamp formats
                timestamp = commit.get("commit", {}).get("committer", {}).get("date")
                if not timestamp:
                    continue
                
                # Parse ISO timestamp and get date part
                if timestamp.endswith('Z'):
                    timestamp = timestamp[:-1] + '+00:00'
                
                dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
                date_str = dt.strftime('%Y-%m-%d')
                activity_dates.add(date_str)
            except (ValueError, AttributeError, KeyError):
                # Skip malformed timestamps
                continue
    
    return activity_dates


def compute_streaks(activity_dates: set[str], until: str) -> StreakStats:
    """
    Compute current and longest activity streaks from activity dates.
    
    Args:
        activity_dates: Set of activity dates in YYYY-MM-DD format
        until: End date for streak computation in YYYY-MM-DD format
        
    Returns:
        StreakStats with current streak, longest streak, and last active date
    """
    if not activity_dates:
        return StreakStats(current=0, longest=0, last_active=None)
    
    # Compute current streak by walking backwards from until date
    current_streak = 0
    last_active = None
    
    try:
        cursor = datetime.fromisoformat(until)
        
        while cursor.strftime('%Y-%m-%d') in activity_dates:
            current_streak += 1
            last_active = cursor.strftime('%Y-%m-%d')
            cursor -= timedelta(days=1)
    except ValueError:
        # Invalid until date format
        pass
    
    # Compute longest streak by scanning sorted dates for contiguous runs
    longest_streak = 0
    current_run = 1
    
    sorted_dates = sorted(activity_dates)
    if not sorted_dates:
        return StreakStats(current=current_streak, longest=0, last_active=last_active)
    
    prev_date = None
    
    for date_str in sorted_dates:
        try:
            current_date = datetime.fromisoformat(date_str)
            
            if prev_date and current_date == prev_date + timedelta(days=1):
                # Consecutive day
                current_run += 1
            else:
                # Gap in dates - check if this run was the longest
                longest_streak = max(longest_streak, current_run)
                current_run = 1
            
            prev_date = current_date
        except ValueError:
            # Skip malformed dates
            continue
    
    # Check the final run
    longest_streak = max(longest_streak, current_run)
    
    return StreakStats(
        current=current_streak,
        longest=longest_streak,
        last_active=last_active
    )


def assign_badges(streaks: StreakStats, total_commits: int) -> List[Badge]:
    """
    Assign badges based on streak stats and commit totals.
    
    Args:
        streaks: StreakStats containing current and longest streak data
        total_commits: Total number of commits in the period
        
    Returns:
        List of earned Badge objects
    """
    badges = []
    
    # Weekly Flame - current streak >= 7 days
    if streaks.current >= 7:
        badges.append(Badge(
            key="weekly_flame",
            label="Weekly Flame",
            emoji="🔥",
            description=f"Active for {streaks.current} consecutive days!"
        ))
    
    # Marathon - longest streak >= 30 days
    if streaks.longest >= 30:
        badges.append(Badge(
            key="marathon",
            label="Marathon Runner",
            emoji="🏃",
            description=f"Longest streak: {streaks.longest} days"
        ))
    
    # Prolific - total commits >= 50
    if total_commits >= 50:
        badges.append(Badge(
            key="prolific",
            label="Prolific Coder",
            emoji="⚡",
            description=f"{total_commits} commits in this period"
        ))
    
    # Welcome Back nudge - current streak is 0 but there was previous activity
    if streaks.current == 0 and streaks.longest > 0:
        badges.append(Badge(
            key="welcome_back",
            label="Welcome Back",
            emoji="👋",
            description="Time to restart your coding streak!"
        ))
    
    # First Steps - for new users with some activity
    if streaks.longest > 0 and streaks.longest < 7 and total_commits < 10:
        badges.append(Badge(
            key="first_steps",
            label="First Steps",
            emoji="🌱",
            description="Great start on your coding journey!"
        ))
    
    return badges


def detect_stale_repos(repos: List[RepoSummary], threshold_days: int) -> List[Tuple[RepoSummary, int]]:
    """
    Detect repositories that haven't been pushed to recently.
    
    Args:
        repos: List of RepoSummary objects
        threshold_days: Number of days after which a repo is considered stale
        
    Returns:
        List of tuples (repo, days_since_push) sorted by days_since_push descending
    """
    stale_repos = []
    # Use naive UTC for consistency with other filters
    now = datetime.utcnow()
    
    for repo in repos:
        if not repo.pushed_at:
            # No push date available - consider very stale
            stale_repos.append((repo, 9999))
            continue
        
        try:
            # Parse the pushed_at timestamp
            pushed_at_str = repo.pushed_at
            if pushed_at_str.endswith('Z'):
                pushed_at_str = pushed_at_str[:-1] + '+00:00'
            
            pushed_at = datetime.fromisoformat(pushed_at_str.replace('Z', '+00:00'))
            # Normalize to naive UTC to avoid naive/aware subtraction issues
            if pushed_at.tzinfo is not None:
                pushed_at = pushed_at.replace(tzinfo=None)
            days_since_push = (now - pushed_at).days
            
            if days_since_push > threshold_days:
                stale_repos.append((repo, days_since_push))
                
        except (ValueError, AttributeError):
            # Malformed date - consider stale
            stale_repos.append((repo, 9999))
    
    # Sort by days since push, descending (most stale first)
    return sorted(stale_repos, key=lambda x: x[1], reverse=True)
