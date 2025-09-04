import time
from typing import Optional
import requests


class GitHubApiError(Exception):
    """Base exception for GitHub API errors"""
    def __init__(self, status: int, message: str):
        self.status = status
        self.message = message
        super().__init__(f"GitHub API error {status}: {message}")


class AuthError(GitHubApiError):
    """Authentication/authorization error (401, 403 without rate limit)"""
    pass


class RateLimitError(GitHubApiError):
    """Rate limit exceeded error (403 with rate limit headers)"""
    def __init__(self, status: int, message: str, reset_epoch: Optional[int] = None):
        self.reset_epoch = reset_epoch
        super().__init__(status, message)


class NotFoundError(GitHubApiError):
    """Resource not found error (404)"""
    pass


def classify_response(response: requests.Response) -> None:
    """
    Classify GitHub API response and raise appropriate exception for error status codes.
    
    Args:
        response: requests.Response object from GitHub API call
        
    Raises:
        AuthError: For 401 (unauthorized)
        RateLimitError: For 403 with rate limit headers
        AuthError: For 403 without rate limit (authorization issue)
        NotFoundError: For 404 (not found)
        GitHubApiError: For other 4xx/5xx errors
    """
    if response.status_code < 400:
        return  # Success, no error to classify
    
    # Get response body for error message (truncated)
    error_text = response.text[:200] if response.text else "No error details"
    
    if response.status_code == 401:
        raise AuthError(
            401, 
            "Unauthorized: check token scope and permissions"
        )
    
    if response.status_code == 403:
        # Check if this is a rate limit error
        rate_limit_remaining = response.headers.get('X-RateLimit-Remaining')
        
        if rate_limit_remaining == '0':
            # This is a rate limit error
            reset_header = response.headers.get('X-RateLimit-Reset')
            reset_epoch = None
            
            if reset_header and reset_header.isdigit():
                try:
                    reset_epoch = int(reset_header)
                except ValueError:
                    pass
            
            raise RateLimitError(
                403,
                "Rate limit exceeded",
                reset_epoch
            )
        else:
            # This is an authorization error (forbidden but not rate limit)
            raise AuthError(
                403,
                "Forbidden: check token permissions and repository access"
            )
    
    if response.status_code == 404:
        raise NotFoundError(404, "Resource not found")
    
    # Generic API error for other 4xx/5xx status codes
    raise GitHubApiError(response.status_code, error_text)


def format_reset_time(reset_epoch: Optional[int]) -> str:
    """
    Format rate limit reset epoch time as a human-readable string.
    
    Args:
        reset_epoch: Unix timestamp when rate limit resets
        
    Returns:
        Human-readable time string or fallback message
    """
    if not reset_epoch:
        return "unknown time"
    
    try:
        reset_time = time.localtime(reset_epoch)
        return time.strftime("%H:%M:%S", reset_time)
    except (OSError, ValueError):
        return "unknown time"