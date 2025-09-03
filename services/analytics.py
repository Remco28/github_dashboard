from datetime import datetime
from typing import List, Set, Optional
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
    now = datetime.utcnow()
    
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