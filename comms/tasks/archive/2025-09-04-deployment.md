# Phase 8 – Optional Deployment

## Goal
Provide simple, repeatable deployment options so users can share the dashboard. Primary target is Streamlit Community Cloud; optional Docker image for self‑hosting.

## Scope
- In: Streamlit Cloud deploy guide and config, environment/secrets mapping, minimal `Dockerfile`, Docker run instructions, README/docs updates.
- Out: CI/CD pipelines, Kubernetes manifests, multi‑stage build optimization beyond minimal needs.

## Files and Targets
- `docs/DEPLOYMENT.md`
  - New: End‑to‑end instructions for Streamlit Cloud and Docker, with screenshots or notes as needed.
- `Dockerfile`
  - New: Minimal image to run `streamlit run app.py` using `python:3.11-slim`.
- `README.md`
  - Update: Add short “Deploy” section pointing to `docs/DEPLOYMENT.md`.

## Detailed Requirements
1) Streamlit Community Cloud
   - Document how to deploy from GitHub repo:
     - App file path: `app.py`.
     - Python version: 3.11 (inherits from runtime or via `requirements.txt`).
     - Secrets: Add `GITHUB_TOKEN`, `GITHUB_USERNAME` in the app’s Secrets manager.
     - Environment variables: Mention that `.env` is ignored; use Streamlit Secrets for production.
     - Caching notes: Rate limits and suggested max repos if hitting limits.
     - Troubleshooting: common permission and rate limit issues.

2) Docker Image (Optional)
   - Provide a minimal, reproducible Dockerfile:
     - Base: `python:3.11-slim`.
     - Copy project files, install via `pip install --no-cache-dir -r requirements.txt`.
     - Expose 8501 and use `CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]`.
   - Document usage:
     - Build: `docker build -t gh-dashboard .`
     - Run: `docker run -p 8501:8501 --env GITHUB_TOKEN=... --env GITHUB_USERNAME=... gh-dashboard`.
     - Optional: Mount `.env` via `--env-file .env` for local runs.

3) README Update
   - Add a brief “Deploy” section referencing `docs/DEPLOYMENT.md`.

## Acceptance Criteria
- `docs/DEPLOYMENT.md` explains Streamlit Cloud deployment with secrets configuration and troubleshooting, plus Docker build/run instructions.
- `Dockerfile` builds successfully and runs the app on port 8501.
- `README.md` contains a Deploy section linking to `docs/DEPLOYMENT.md`.

## Constraints
- Do not commit secrets; reference Streamlit Secrets or environment variables.
- Keep Docker image minimal; no OS package bloat unless strictly required.

## Guidance / Pseudocode
- `Dockerfile` (outline):
  ```dockerfile
  FROM python:3.11-slim
  WORKDIR /app
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  COPY . .
  EXPOSE 8501
  CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
  ```
- `docs/DEPLOYMENT.md` sections:
  - Streamlit Cloud (steps to deploy, set Secrets, configure app path)
  - Docker (build/run, env vars, `.env` usage for local)
  - Troubleshooting and rate limit tips

