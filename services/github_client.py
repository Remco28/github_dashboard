import requests
from typing import Dict, List
from models.github_types import RepoSummary

GITHUB_API = "https://api.github.com"


def parse_next_link(link_header: str | None) -> str | None:
    """Parse the Link header to extract the next page URL."""
    if not link_header:
        return None
    
    links = link_header.split(',')
    for link in links:
        parts = link.strip().split(';')
        if len(parts) == 2:
            url = parts[0].strip('<>')
            rel = parts[1].strip()
            if 'rel="next"' in rel:
                return url
    return None


def list_user_repos(username: str, token: str, include_private: bool = True) -> List[Dict]:
    """List repositories for the authenticated user with pagination."""
    url = f"{GITHUB_API}/user/repos?per_page=100&type=owner&sort=pushed"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    
    repos = []
    while url:
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code >= 400:
            error_text = response.text[:200] if response.text else "No error details"
            raise RuntimeError(
                f"GitHub API error {response.status_code}: {error_text}"
            )
        
        page_repos = response.json()
        repos.extend(page_repos)
        
        # Get next page URL from Link header
        url = parse_next_link(response.headers.get("Link"))
    
    return repos


def to_repo_summary(repo: Dict) -> RepoSummary:
    """Convert raw repo dict to RepoSummary dataclass."""
    return RepoSummary(
        name=repo["name"],
        full_name=repo["full_name"],
        private=repo["private"],
        stargazers_count=repo.get("stargazers_count", 0),
        forks_count=repo.get("forks_count", 0),
        open_issues_count=repo.get("open_issues_count", 0),
        pushed_at=repo.get("pushed_at", ""),
        language=repo.get("language"),
        html_url=repo.get("html_url", ""),
        archived=repo.get("archived", False),
        disabled=repo.get("disabled", False),
        default_branch=repo.get("default_branch", "main")
    )


def get_repo_languages(owner: str, repo: str, token: str) -> Dict[str, int]:
    """Get language statistics for a repository."""
    url = f"{GITHUB_API}/repos/{owner}/{repo}/languages"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 404:
        return {}
    
    if response.status_code >= 400:
        error_text = response.text[:200] if response.text else "No error details"
        raise RuntimeError(
            f"GitHub API error {response.status_code}: {error_text}"
        )
    
    return response.json()


def list_repo_commits(owner: str, repo: str, token: str, since: str, until: str, max_pages: int = 2) -> List[Dict]:
    """
    List commits for a repository within a time window with bounded pagination.
    
    Args:
        owner: Repository owner
        repo: Repository name
        token: GitHub token
        since: ISO datetime string (start of window)
        until: ISO datetime string (end of window)  
        max_pages: Maximum number of pages to fetch (default 2 to limit API calls)
        
    Returns:
        List of commit dictionaries
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/commits"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    params = {
        "since": since,
        "until": until,
        "per_page": 100
    }
    
    commits = []
    pages_fetched = 0
    
    while url and pages_fetched < max_pages:
        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code == 404:
            # Repository might be empty or not accessible
            break
            
        if response.status_code >= 400:
            error_text = response.text[:200] if response.text else "No error details"
            raise RuntimeError(
                f"GitHub API error {response.status_code}: {error_text}"
            )
        
        page_commits = response.json()
        commits.extend(page_commits)
        
        pages_fetched += 1
        
        # Get next page URL from Link header
        url = parse_next_link(response.headers.get("Link"))
        # Clear params for subsequent requests since URL contains them
        params = None
    
    return commits


def get_file_contents(owner: str, repo: str, path: str, token: str) -> dict | None:
    """
    Get file contents from a repository via the GitHub Contents API.
    
    Args:
        owner: Repository owner
        repo: Repository name  
        path: Path to the file within the repository
        token: GitHub token
        
    Returns:
        Response JSON dict if file exists, None if 404 (file not found)
    """
    url = f"{GITHUB_API}/repos/{owner}/{repo}/contents/{path}"
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github+json"
    }
    
    response = requests.get(url, headers=headers, timeout=10)
    
    if response.status_code == 404:
        return None
    
    if response.status_code >= 400:
        error_text = response.text[:200] if response.text else "No error details"
        raise RuntimeError(
            f"GitHub API error {response.status_code}: {error_text}"
        )
    
    return response.json()