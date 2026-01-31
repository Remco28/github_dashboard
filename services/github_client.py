import requests
import time
from typing import Dict, List
from models.github_types import RepoSummary
from services.errors import classify_response, NotFoundError

GITHUB_API = "https://api.github.com"


def _request_with_retry(method: str, url: str, headers: dict, params: dict = None, max_retries: int = 2, backoff: float = 0.5) -> requests.Response:
    """
    Make HTTP request with bounded retries for transient failures.

    Args:
        method: HTTP method (GET, POST, etc.)
        url: Request URL
        headers: Request headers
        params: Query parameters
        max_retries: Maximum number of retry attempts
        backoff: Backoff delay in seconds between retries

    Returns:
        Response object

    Raises:
        Exception: For non-transient errors or after max retries
    """
    last_exception = None

    for attempt in range(max_retries + 1):
        try:
            response = requests.request(method, url, headers=headers, params=params, timeout=10)
            # Classify response for API errors
            classify_response(response)
            return response

        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as e:
            last_exception = e
            if attempt < max_retries:
                time.sleep(backoff)
                continue
            else:
                raise e
        except Exception as e:
            # For API errors (AuthError, RateLimitError, etc.), don't retry
            raise e

    # This shouldn't be reached, but just in case
    if last_exception:
        raise last_exception


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
        response = _request_with_retry("GET", url, headers)

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

    try:
        response = _request_with_retry("GET", url, headers)
        return response.json()
    except NotFoundError:
        # Repository not found or no language data - return empty dict
        return {}


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
        try:
            response = _request_with_retry("GET", url, headers, params)

            page_commits = response.json()
            commits.extend(page_commits)

            pages_fetched += 1

            # Get next page URL from Link header
            url = parse_next_link(response.headers.get("Link"))
            # Clear params for subsequent requests since URL contains them
            params = None

        except NotFoundError:
            # Repository might be empty or not accessible
            break

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

    try:
        response = _request_with_retry("GET", url, headers)
        return response.json()
    except NotFoundError:
        # File not found - return None
        return None
