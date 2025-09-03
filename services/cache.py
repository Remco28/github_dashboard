import time
import functools
from typing import Dict, Tuple, Any, Callable


# Global cache store
_cache_store: Dict[Any, Tuple[float, Any]] = {}


def ttl_cache(ttl_seconds: int) -> Callable:
    """
    TTL cache decorator that caches function results for a specified time.
    
    Args:
        ttl_seconds: Time to live in seconds for cached values
        
    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Create cache key from function name and arguments
            try:
                # Only use hashable arguments for the cache key
                cache_key = (func.__name__, args, tuple(sorted(kwargs.items())))
            except TypeError:
                # If arguments are not hashable, skip caching
                return func(*args, **kwargs)
            
            now = time.time()
            
            # Check if we have a cached result that hasn't expired
            if cache_key in _cache_store:
                expires_at, cached_value = _cache_store[cache_key]
                if now < expires_at:
                    return cached_value
            
            # Call the function and cache the result
            result = func(*args, **kwargs)
            _cache_store[cache_key] = (now + ttl_seconds, result)
            
            return result
        
        return wrapper
    return decorator


# Cached wrapper for list_user_repos with 5-minute TTL
@ttl_cache(300)  # 5 minutes
def cached_list_user_repos(username: str, token: str, cache_bust: str = None) -> list:
    """Cached version of list_user_repos. cache_bust parameter can be used to bypass cache."""
    from services.github_client import list_user_repos
    return list_user_repos(username, token)


# Cached wrapper for list_repo_commits with 5-minute TTL
@ttl_cache(300)  # 5 minutes
def cached_list_repo_commits(owner: str, repo: str, token: str, since: str, until: str) -> list:
    """Cached version of list_repo_commits."""
    from services.github_client import list_repo_commits
    return list_repo_commits(owner, repo, token, since, until)