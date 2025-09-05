# Phase 10 – NEXT_STEPS Scalability Enhancement

## Overview
Enhance NEXT_STEPS processing to support more than 20 repositories while maintaining performance and respecting rate limits. Add configurability, smart prioritization, and improved UX for large repository sets.

## Goals
- Support processing 50-100+ repositories for NEXT_STEPS
- Make the limit user-configurable with appropriate warnings
- Prioritize recently active repositories
- Improve dropdown UX for large repo counts
- Maintain rate limit compliance

## Scope
- Modify `app.py` NEXT_STEPS section to use configurable limit
- Add sidebar control for NEXT_STEPS processing limit
- Implement smart sorting (recent activity first)
- Add rate limit warnings and progress indicators
- Enhance repository selector dropdown with search/filter
- Update cache strategy for larger datasets

## Deliverables
- `app.py`: Configurable NEXT_STEPS processing with smart prioritization
- `ui/components.py`: Enhanced repository selector with search capability
- Updated cache handling for larger NEXT_STEPS datasets
- Rate limit warnings and progress feedback

## Acceptance Criteria
- Sidebar slider controls NEXT_STEPS processing limit (10-100 repos)
- Repositories sorted by recent push date for processing
- Warning shown when approaching rate limits
- Dropdown supports search/filter for 100+ repos
- Processing shows progress for large sets
- Cache hit rate maintained for repeated loads
- No regressions in existing functionality

## Technical Details
- Use `st.slider` for configurable limit with default 20
- Sort repos by `pushed_at` descending before slicing
- Add `st.progress` and `st.spinner` for large processing
- Implement dropdown search using `st.selectbox` with filtered options
- Extend cache TTL for NEXT_STEPS data to 10 minutes
- Add rate limit check before processing large sets

## Risks
- Rate limit exhaustion with large repo counts
- UI slowdown with 100+ dropdown options
- Memory usage for large cached datasets

## Mitigation
- Rate limit warnings and processing caps
- Efficient caching and lazy loading
- Progress indicators for user feedback
- Fallback to cached data on errors

## Testing
- Test with 50+ repositories
- Verify rate limit handling
- Check dropdown performance with 100 options
- Validate cache behavior with large datasets