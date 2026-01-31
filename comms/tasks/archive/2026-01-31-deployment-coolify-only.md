# Spec: Deployment Docs — Coolify Only

Owner: Architect  
Date: 2026-01-31  
Status: SPEC READY

## Goal
Align deployment documentation with the current workflow: Coolify (Nixpacks) on a Hetzner VPS. Remove Streamlit Community Cloud references.

## Scope
### In Scope
- Remove Streamlit Community Cloud instructions from docs.
- Keep Coolify/Nixpacks instructions as the only deployment path.
- Ensure the Procfile-based start command is documented.
- Remind operators to set `GITHUB_TOKEN` and `GITHUB_USERNAME` in Coolify.

### Out of Scope
- Any Docker workflow or Dockerfile references.

## Files to Update (Expected)
- `docs/DEPLOYMENT.md`
- `README.md`
- `docs/ROADMAP.md` (if it references Streamlit Cloud)

## Requirements
1. **docs/DEPLOYMENT.md**
   - Remove Streamlit Community Cloud section entirely.
   - Keep a single Coolify-focused guide (Nixpacks).
   - Mention Procfile and `$PORT` usage.
2. **README.md**
   - Remove Streamlit Cloud references.
   - Keep deployment section pointing to Coolify-only guide.
3. **ROADMAP**
   - Remove any mention of Streamlit Cloud deployment if still present.

## Acceptance Criteria
- No Streamlit Cloud references remain in repo docs.
- Deployment docs clearly describe Coolify + Nixpacks flow and env vars.
- Procfile usage is documented as the app start command.
