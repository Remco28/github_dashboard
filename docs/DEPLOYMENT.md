# Deployment Guide

This guide provides step-by-step instructions for deploying the GitHub Repository Dashboard using Coolify with Nixpacks on a Hetzner VPS (or similar).

## Prerequisites

Before deploying, ensure you have:
- A GitHub repository containing this project
- A GitHub Personal Access Token with appropriate scopes
- Your GitHub username
- A Coolify instance (self-hosted or managed)

## Coolify Deployment (Nixpacks)

Coolify builds and deploys this app directly from GitHub using Nixpacks. No Dockerfile is required.

### Step 1: Prepare Your Repository

1. **Push your changes** to GitHub
2. **Ensure** the default branch is `main`
3. **Confirm** a `Procfile` exists at the repo root (see below)

### Step 2: Procfile

The repository includes a `Procfile` that tells Nixpacks how to start the app:

```
web: streamlit run app.py --server.address=0.0.0.0 --server.port=$PORT
```

This binds the Streamlit server to `0.0.0.0` and uses the `$PORT` environment variable injected by Coolify.

### Step 3: Create the App in Coolify

1. **Create a new Application** in your Coolify dashboard
2. **Connect GitHub** and select this repository
3. **Set Build Pack:** Nixpacks
4. **Branch:** `main`

### Step 4: Configure Environment Variables

**Important:** Do NOT commit your `.env` file or expose secrets in your repository.

Set these environment variables in Coolify:

| Variable | Description |
|----------|-------------|
| `GITHUB_TOKEN` | Your GitHub Personal Access Token |
| `GITHUB_USERNAME` | Your GitHub username |

### Step 5: Deploy

1. **Start the build** in Coolify
2. **Verify** the app loads at the assigned URL
3. **Check logs** if any issues arise

## Coolify Notes

- **Automatic Deploys:** App redeploys automatically on push to `main`
- **Dependencies:** Installed automatically from `requirements.txt`
- **Secrets:** Always use Coolify environment variables (never commit `.env`)
- **Port:** Handled automatically via `$PORT` in the Procfile

## Rate Limit Management

GitHub API rate limits apply:

- **Authenticated Rate Limit:** 5,000 requests/hour
- **Recommendations:**
  - Start with "Max Repositories for Charts" set to 5-10
  - Use the cache system effectively (avoid unnecessary bypasses)
  - Monitor rate limit messages in the application

## Troubleshooting

### Authentication Errors
- Verify your `GITHUB_TOKEN` is valid and not expired
- Check token scopes: `repo` for private repos, `public_repo` for public only
- Ensure `GITHUB_USERNAME` matches your GitHub username exactly

### Rate Limiting Issues
- Reduce "Max Repositories for Charts" in the sidebar
- Wait for rate limit reset (GitHub provides 5,000 requests/hour for authenticated users)
- Use cache controls wisely

### App Not Starting
- Check Coolify build logs for errors
- Verify the Procfile exists and has correct syntax
- Ensure `requirements.txt` is present and valid

## Support

If you encounter deployment issues:

1. **Check the logs** in Coolify
2. **Verify your configuration** against this guide
3. **Test locally first** to isolate deployment-specific issues
4. **Check GitHub API status** if experiencing data loading issues

For additional support, refer to:
- [Coolify Documentation](https://coolify.io/docs)
- [GitHub API Documentation](https://docs.github.com/en/rest)
