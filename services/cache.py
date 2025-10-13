import time
import functools
from typing import Dict, Tuple, Any, Callable, Optional


# Global cache store
_cache_store: Dict[Any, Tuple[float, Any]] = {}

# Cache telemetry metrics
_cache_metrics: Dict[str, Dict[str, int]] = {}


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
            # Handle cache_bust parameter
            cache_bust_value = kwargs.pop('cache_bust', None)

            # Create cache key from function name and arguments
            try:
                # Only use hashable arguments for the cache key
                base_key = (func.__name__, args, tuple(sorted(kwargs.items())))
                if cache_bust_value is not None:
                    cache_key = (base_key, cache_bust_value)
                else:
                    cache_key = base_key
            except TypeError:
                # If arguments are not hashable, skip caching
                return func(*args, **kwargs)

            now = time.time()

            # Initialize metrics for this function if not exists
            if func.__name__ not in _cache_metrics:
                _cache_metrics[func.__name__] = {'hits': 0, 'misses': 0}

            # Check if we have a cached result that hasn't expired
            if cache_key in _cache_store:
                expires_at, cached_value = _cache_store[cache_key]
                if now < expires_at:
                    _cache_metrics[func.__name__]['hits'] += 1
                    return cached_value

            # Cache miss
            _cache_metrics[func.__name__]['misses'] += 1

            # Call the function and cache the result
            result = func(*args, **kwargs)
            _cache_store[cache_key] = (now + ttl_seconds, result)

            return result

        return wrapper
    return decorator


# Cached wrapper for list_user_repos with 5-minute TTL
@ttl_cache(300)  # 5 minutes
def cached_list_user_repos(username: str, token: str, cache_bust: Optional[str] = None) -> list:
    """Cached version of list_user_repos. cache_bust parameter can be used to bypass cache."""
    from services.github_client import list_user_repos
    return list_user_repos(username, token)


# Cached wrapper for list_repo_commits with 5-minute TTL
@ttl_cache(300)  # 5 minutes
def cached_list_repo_commits(owner: str, repo: str, token: str, since: str, until: str, cache_bust: Optional[str] = None) -> list:
    """Cached version of list_repo_commits."""
    from services.github_client import list_repo_commits
    return list_repo_commits(owner, repo, token, since, until)


# Cached wrapper for get_file_contents with 5-minute TTL
@ttl_cache(300)  # 5 minutes
def cached_get_file_contents(owner: str, repo: str, path: str, token: str) -> dict | None:
    """Cached version of get_file_contents."""
    from services.github_client import get_file_contents
    return get_file_contents(owner, repo, path, token)


# Cached wrapper for fetch_next_steps with 10-minute TTL
@ttl_cache(600)  # 10 minutes
def cached_fetch_next_steps(owner: str, repo: str, token: str, cache_bust: Optional[str] = None) -> str | None:
    """Cached version of fetch_next_steps."""
    from services.next_steps import fetch_next_steps
    return fetch_next_steps(owner, repo, token)


def clear_cache() -> None:
    """Clear all cached data from the in-memory cache store."""
    global _cache_store
    _cache_store.clear()


def cache_stats() -> Dict[str, Any]:
    """
    Get basic statistics about the current cache state.

    Returns:
        Dictionary with cache statistics (no PII or secret values)
    """
    if not _cache_store:
        return {
            "count": 0,
            "keys": [],
            "earliest_expiry": None,
            "latest_expiry": None
        }

    now = time.time()
    active_entries = []

    # Find active (non-expired) entries
    for key, (expires_at, value) in _cache_store.items():
        if expires_at > now:
            active_entries.append((key, expires_at))

    if not active_entries:
        return {
            "count": 0,
            "keys": [],
            "earliest_expiry": None,
            "latest_expiry": None
        }

    # Extract function names from cache keys for safe display
    safe_keys = []
    for key_tuple, _ in active_entries:
        if isinstance(key_tuple, tuple) and len(key_tuple) > 0:
            func_name = key_tuple[0] if isinstance(key_tuple[0], str) else "unknown"
            safe_keys.append(func_name)

    # Get expiry times
    expiry_times = [expires_at for _, expires_at in active_entries]

    return {
        "count": len(active_entries),
        "keys": list(set(safe_keys)),  # Unique function names
        "earliest_expiry": min(expiry_times),
        "latest_expiry": max(expiry_times)
    }


def cache_metrics() -> Dict[str, Any]:
    """
    Get cache telemetry metrics.

    Returns:
        Dictionary with cache hit/miss metrics
    """
    # Compute totals
    total_hits = sum(func_data['hits'] for func_data in _cache_metrics.values())
    total_misses = sum(func_data['misses'] for func_data in _cache_metrics.values())
    total_requests = total_hits + total_misses
    hit_rate = (total_hits / total_requests) if total_requests > 0 else 0.0

    # Get top 3 functions by hits
    sorted_funcs = sorted(_cache_metrics.items(), key=lambda x: x[1]['hits'], reverse=True)
    top_3 = sorted_funcs[:3]

    return {
        "total_hits": total_hits,
        "total_misses": total_misses,
        "hit_rate": hit_rate,
        "per_func": dict(_cache_metrics),  # Copy of the metrics
        "top_3_by_hits": [(name, data['hits']) for name, data in top_3]
    }
