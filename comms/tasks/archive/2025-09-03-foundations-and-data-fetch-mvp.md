# Task Spec: Foundations and Data Fetch MVP (Phases 0–1)

Author: Architect
Date: 2025-09-03
Status: SPEC READY

## Summary
Implement project foundations and a minimal data fetch layer to retrieve GitHub repository metadata for the authenticated user. Deliver a bootable Streamlit app stub that loads configuration and shows a minimal summary derived from live GitHub data. This work seeds later UI and analytics phases.

## Objectives
- Load configuration securely from environment (.env) with PAT and username.
- Implement a GitHub API client with pagination and basic error handling.
- Fetch repositories and essential metadata efficiently with simple caching.
- Provide a minimal Streamlit entry that exercises the client and displays basic info.

## User Stories
- As a user, I can provide my GitHub token and username via .env and run the app without code changes.
- As a user, I can see how many repositories I own and a simple table with key fields.
- As a user, the app remains responsive and avoids repeated API calls on simple refreshes.

## In Scope
- Config loading, repo layout scaffolding, requirements.
- GitHub REST calls for listing user repositories and fetching languages per repo (optional for Phase 1 UI, but implement function now).
- Minimal caching (in‑memory TTL) to reduce rate‑limit pressure.

## Out of Scope (defer)
- Advanced charts/visualizations (Phase 3).
- NEXT_STEPS.md parsing (Phase 4).
- Gamification/Badges (Phase 5).

## Files and Functions
Create the following files and implement the specified functions. Keep code clear and idiomatic. Add type hints.

- `requirements.txt`
  - Include: `streamlit`, `requests`, `pandas`, `plotly`, `python-dotenv`.
  - Optional now: `cachetools` (or implement a simple TTL cache yourself).

- `.env.example`
  - Keys: `GITHUB_TOKEN=`, `GITHUB_USERNAME=`.
  - Comment that token needs `repo` scope to access private repos.

- `.gitignore`
  - Ensure `.env` is ignored.

- `config/settings.py`
  - `from dataclasses import dataclass`
  - `@dataclass class Settings: github_token: str; github_username: str`
  - `def get_settings() -> Settings:` loads `.env` (via `dotenv.load_dotenv()`), validates presence, raises friendly `RuntimeError` if missing.

- `models/github_types.py`
  - `@dataclass class RepoSummary:`
    - fields: `name: str`, `full_name: str`, `private: bool`, `stargazers_count: int`, `forks_count: int`, `open_issues_count: int`, `pushed_at: str`, `language: str | None`, `html_url: str`, `archived: bool`, `disabled: bool`, `default_branch: str`.

- `services/github_client.py`
  - `GITHUB_API = "https://api.github.com"`
  - `def list_user_repos(username: str, token: str, include_private: bool = True) -> list[dict]:`
    - Calls `GET /user/repos` with `per_page=100`, `type=owner`, `sort=pushed`.
    - Uses `Authorization: token <PAT>` header.
    - Paginates via `Link` header until no `rel="next"`.
    - Returns a list of raw repo dicts (serialize minimally here; transform later).
  - `def to_repo_summary(repo: dict) -> RepoSummary:` maps subset of fields to dataclass.
  - `def get_repo_languages(owner: str, repo: str, token: str) -> dict[str, int]:` calls `GET /repos/{owner}/{repo}/languages` and returns the language byte map. Handle 404 gracefully (empty dict).
  - Basic error handling: raise `RuntimeError` with concise message on non‑2xx; include status code, not token.
  - Timeouts: pass a short timeout (e.g., 10s) to requests.

- `services/cache.py` (simple)
  - Provide `ttl_cache(ttl_seconds: int)` decorator using a dict of `{key: (expires_at, value)}` and `functools.wraps`. Key by function name + args + kwargs (only hashables). For unsafe args, skip caching.
  - Use on `list_user_repos` at 300s by default (or expose a cached wrapper that calls the underlying function).

- `app.py` (minimal Streamlit stub)
  - Loads settings via `get_settings()`.
  - Calls cached `list_user_repos` and converts to `RepoSummary` list.
  - Displays: title, a stat showing repo count, and a small `st.dataframe` with selected columns: name, private, stars, forks, open_issues, pushed_at, language.
  - Provide a `Refresh` button that bypasses cache for that call (e.g., `cache_bust` query param in key or a manual flag to the cached function).

## API Endpoints
- `GET https://api.github.com/user/repos?per_page=100&type=owner&sort=pushed` — list repos for the authenticated user; paginated.
- `GET https://api.github.com/repos/{owner}/{repo}/languages` — language byte counts.
- Headers: `Authorization: token <PAT>`, `Accept: application/vnd.github+json`.

## Constraints & Non‑functional Requirements
- Security: Never log tokens; do not echo secrets to UI.
- Resilience: Handle 401 (bad token), 403 (rate‑limited), 404 (missing resource) with user‑readable errors in Streamlit.
- Performance: Avoid blocking UI with repeated network calls; use caching and minimal transforms.
- Compatibility: Python 3.10+ preferred; keep dependencies modest.

## Pseudocode & Notes

Pagination (list_user_repos):
```
url = f"{GITHUB_API}/user/repos?per_page=100&type=owner&sort=pushed"
headers = {"Authorization": f"token {token}", "Accept": "application/vnd.github+json"}
repos = []
while url:
    resp = requests.get(url, headers=headers, timeout=10)
    if resp.status_code >= 400:
        raise RuntimeError(f"GitHub API error {resp.status_code}: {resp.text[:200]}")
    repos.extend(resp.json())
    url = parse_next_link(resp.headers.get("Link"))  # returns None if no next
return repos
```

TTL cache decorator:
```
store = {}

def ttl_cache(ttl):
    def deco(fn):
        @wraps(fn)
        def wrapper(*args, **kwargs):
            key = (fn.__name__, args, tuple(sorted(kwargs.items())))
            now = time.time()
            if key in store:
                exp, val = store[key]
                if now < exp:
                    return val
            val = fn(*args, **kwargs)
            store[key] = (now + ttl, val)
            return val
        return wrapper
    return deco
```

RepoSummary mapping:
```
return RepoSummary(
  name=d["name"], full_name=d["full_name"], private=d["private"],
  stargazers_count=d.get("stargazers_count", 0), forks_count=d.get("forks_count", 0),
  open_issues_count=d.get("open_issues_count", 0), pushed_at=d.get("pushed_at", ""),
  language=d.get("language"), html_url=d.get("html_url", ""), archived=d.get("archived", False),
  disabled=d.get("disabled", False), default_branch=d.get("default_branch", "main")
)
```

Refresh button pattern:
```
if st.button("Refresh"):
    cache_bust = str(time.time())  # pass as dummy arg to change cache key
else:
    cache_bust = None
raw = cached_list_user_repos(username, token, cache_bust)
```

## Acceptance Criteria
- Running `streamlit run app.py` launches without errors when `.env` is set.
- App reads `GITHUB_TOKEN` and `GITHUB_USERNAME` from env; missing values produce a clear error.
- App displays total repository count and a table with at least 7 columns described above.
- Pagination works: if the user has >100 repos, the count matches GitHub web UI within one page refresh.
- Caching: repeated renders within 5 minutes do not re‑issue `GET /user/repos` calls (visible via a simple console log counter or debug flag).
- Error handling: invalid token shows a user‑friendly message and does not crash the app.

## Manual Test Plan
1) Setup: Copy `.env.example` to `.env`, fill `GITHUB_TOKEN` (with `repo` scope) and `GITHUB_USERNAME`.
2) Install deps: `pip install -r requirements.txt`.
3) Run: `streamlit run app.py`.
4) Verify: Title loads, repo count > 0 (for active accounts), table visible.
5) Refresh: Click Refresh; data updates without error; quickly refresh again and observe no API re‑hit within TTL window.
6) Negative: Remove/blank token; app shows instructive error about configuration.

## Notes for Developer
- Keep functions small and testable. Consider extracting `parse_next_link(link_header: str|None) -> str|None` as a helper.
- Be mindful of GitHub rate limiting; do not add aggressive background refresh.
- Add minimal logging (INFO level) without secrets.
- Prefer returning simple Python types or dataclasses from services; avoid Streamlit coupling in the services layer.

## Deliverables
- Implemented files as listed.
- The app demonstrates live data retrieval and minimal display.
- Short usage notes appended to README (optional, nice‑to‑have at this stage).

