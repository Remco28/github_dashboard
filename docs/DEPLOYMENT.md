# 🚢 Deployment Guide

This guide provides step-by-step instructions for deploying the GitHub Project Tracker Dashboard using Streamlit Community Cloud or Docker.

## 📋 Prerequisites

Before deploying, ensure you have:
- A GitHub repository containing this project
- A GitHub Personal Access Token with appropriate scopes
- Your GitHub username

## 🌐 Streamlit Community Cloud Deployment (Recommended)

Streamlit Community Cloud provides free hosting for Streamlit applications directly from your GitHub repository.

### Step 1: Prepare Your Repository

1. **Fork or clone** this repository to your GitHub account
2. **Push your changes** if you've made any local modifications
3. **Ensure** your repository is public (or you have a Streamlit Community Cloud plan that supports private repos)

### Step 2: Deploy on Streamlit Community Cloud

1. **Visit** [share.streamlit.io](https://share.streamlit.io)
2. **Sign in** with your GitHub account
3. **Click "New app"**
4. **Configure your app:**
   - **Repository:** Select your forked repository
   - **Branch:** `main` (or your default branch)
   - **Main file path:** `app.py`
   - **App URL:** Choose a custom URL (optional)

### Step 3: Configure Secrets

**Important:** Do NOT commit your `.env` file or expose secrets in your repository.

1. **After deployment**, click on your app's settings (⚙️ icon)
2. **Navigate to "Secrets"**
3. **Add the following secrets:**

```toml
[secrets]
GITHUB_TOKEN = "your_github_personal_access_token_here"
GITHUB_USERNAME = "your_github_username_here"
```

**Note:** Use the TOML format in the Streamlit Secrets manager, not the `.env` format.

### Step 4: Verify Deployment

1. **Visit your app URL** (provided after deployment)
2. **Check that repositories load** correctly
3. **Test filtering and visualization** features
4. **Verify theme toggle** works properly

### Streamlit Cloud Configuration Notes

- **Python Version:** 3.11 (inherits from runtime or via requirements.txt)
- **Dependencies:** Installed automatically from `requirements.txt`
- **Environment Variables:** Use Streamlit Secrets instead of `.env` files
- **Automatic Updates:** App redeploys automatically when you push to your repository
- **Caching Notes:** Rate limits may require reducing "Max Repositories for Charts"
- **Performance:** Use "Bypass Cache" sparingly to preserve API rate limits

### Streamlit Cloud Troubleshooting

**Authentication Errors**
- Verify your `GITHUB_TOKEN` is valid and not expired
- Check token scopes: `repo` for private repos, `public_repo` for public only
- Ensure `GITHUB_USERNAME` matches your GitHub username exactly

**Rate Limiting Issues**
- Reduce "Max Repositories for Charts" in the sidebar (try 5 instead of 20)
- Wait for rate limit reset (GitHub provides 5000 requests/hour for authenticated users)
- Use cache controls wisely - avoid frequent cache bypassing

**Empty States**
- Confirm your GitHub username is spelled correctly
- Verify your token has access to the repositories you expect
- Check the app logs in Streamlit Cloud dashboard for detailed error messages

## 🐳 Docker Deployment (Self-Hosting)

Use Docker for self-hosting or when you need more control over the deployment environment.

### Step 1: Build the Docker Image

```bash
# Clone the repository (if not already done)
git clone <your-repository-url>
cd github_dashboard

# Build the Docker image
docker build -t gh-dashboard .
```

### Step 2: Run with Environment Variables

**Option 1: Using command line environment variables**
```bash
docker run -p 8501:8501 \
  -e GITHUB_TOKEN="your_github_personal_access_token_here" \
  -e GITHUB_USERNAME="your_github_username_here" \
  gh-dashboard
```

**Option 2: Using environment file (recommended for local development)**
```bash
# Create .env file (if not already present)
cp .env.example .env
# Edit .env with your credentials

# Run with environment file
docker run -p 8501:8501 --env-file .env gh-dashboard
```

### Step 3: Access the Application

- **Open your browser** and navigate to `http://localhost:8501`
- **The dashboard** should load with your GitHub repositories

### Docker Configuration Details

The Docker image:
- **Base Image:** `python:3.11-slim` for minimal size
- **Working Directory:** `/app`
- **Exposed Port:** 8501 (Streamlit default)
- **Entry Point:** `streamlit run app.py --server.port=8501 --server.address=0.0.0.0`

### Docker Troubleshooting

**Build Failures**
- Ensure Docker is installed and running
- Check that all files are present in the build context
- Verify `requirements.txt` is valid

**Container Won't Start**
- Check that port 8501 is not already in use: `lsof -i :8501`
- Verify environment variables are set correctly
- Check container logs: `docker logs <container-id>`

**Configuration Errors**
- Ensure environment variables are provided; the app will show a configuration error if missing
- Verify `.env` file format matches `.env.example`
- Check that your GitHub token has appropriate permissions

## 🔧 Performance & Rate Limit Management

Both deployment methods should consider GitHub API rate limits:

- **Authenticated Rate Limit:** 5000 requests/hour
- **Unauthenticated Rate Limit:** 60 requests/hour
- **Recommendations:**
  - Start with "Max Repositories for Charts" set to 5-10
  - Use the cache system effectively (don't bypass unnecessarily)
  - Monitor rate limit messages in the application
  - Consider the total number of repositories when setting limits

## 📞 Support

If you encounter deployment issues:

1. **Check the logs** (Streamlit Cloud dashboard or `docker logs`)
2. **Verify your configuration** against this guide  
3. **Test locally first** to isolate deployment-specific issues
4. **Check GitHub API status** if experiencing data loading issues

For additional support, refer to:
- [Streamlit Community Cloud Documentation](https://docs.streamlit.io/streamlit-community-cloud)
- [Docker Documentation](https://docs.docker.com/)
- [GitHub API Documentation](https://docs.github.com/en/rest)

