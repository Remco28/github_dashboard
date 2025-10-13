# 📊 GitHub Repository Dashboard

A comprehensive Streamlit dashboard that provides insights into your GitHub repositories, including visualizations, activity tracking, and productivity features to help you stay motivated and organized.

## ✨ Features

- **Repository Overview**: Browse all your repositories with detailed stats, relative “Last Push” timings, and filtering options
- **Interactive Visualizations**: Language distribution, commit trends, activity heatmaps, and per-repository analytics
- **NEXT_STEPS Integration**: Parse and display NEXT_STEPS.md files from your repositories with task aggregation, configurable processing limits (10-100 repos), and smart prioritization (preferred path `comms/NEXT_STEPS.md`, root fallback supported)
- **Smart Caching**: Intelligent caching system to respect GitHub API rate limits
- **Per‑Section Refresh**: Refresh Visualizations or NEXT_STEPS independently without clearing the whole cache
- **Cache Telemetry**: Sidebar shows cache hits, misses, hit rate, and top cached functions (no PII)
- **Settings Help**: Built-in guidance for setup and troubleshooting

## 🚀 Quickstart

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd github_dashboard
   ```

2. **Create virtual environment (optional but recommended)**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up configuration**
   ```bash
   cp .env.example .env
   # Edit .env file with your GitHub credentials
   ```

5. **Run the application**
   ```bash
   streamlit run app.py
   ```

The dashboard will open in your web browser at `http://localhost:8501`.

## ⚙️ Configuration

### Environment Variables

Create a `.env` file in the project root with the following variables:

```env
# GitHub Configuration
# Create a personal access token with 'repo' scope to access private repositories
GITHUB_TOKEN=your_github_personal_access_token
GITHUB_USERNAME=your_github_username
```

### Theming (optional)

You can adjust the app’s look using Streamlit’s config file at `.streamlit/config.toml`:

```
[theme]
base = "light"
primaryColor = "#1f77b4"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F6F8FA"
textColor = "#262730"
font = "sans serif"
```

Notes:
- Theme controls colors and font globally without custom CSS.
- It doesn’t hide header controls (menu/deploy) or reposition Plotly toolbars; those were handled with targeted CSS.
- Adjusting theme can reduce custom CSS surface area for future tweaks.

### GitHub Token Setup

1. Go to GitHub Settings → Developer settings → Personal access tokens
2. Click "Generate new token (classic)"
3. Select scopes:
   - `public_repo` - For access to public repositories only
   - `repo` - For access to both public and private repositories (recommended)
4. Copy the generated token and add it to your `.env` file
5. Ensure your `.env` file is in `.gitignore` to keep your token secure

### Token Permissions

- **Public repositories only**: `public_repo` scope
- **All repositories (recommended)**: `repo` scope
- **Rate limits**: 5,000 requests/hour (authenticated), 60 requests/hour (unauthenticated)

## 🔧 Running the Application

Once configured, start the dashboard:

```bash
streamlit run app.py
```

The application will:
1. Load your GitHub configuration
2. Fetch repository data (cached for performance)
3. Display interactive dashboard with multiple sections:
   - Repository statistics and table
   - Visual analytics and charts
   - NEXT_STEPS task integration

## Testing

This project uses pytest for automated testing.

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-mock

# Run all tests
pytest tests/

# Run with verbose output
pytest tests/ -v

# Run specific test file
pytest tests/test_analytics.py
```

### Writing Tests

Tests are located in the `tests/` directory. Use `pytest-mock` for mocking external dependencies like GitHub API calls.

## 🛠️ Troubleshooting

### Common Issues

**Authentication Errors**
- Verify your `GITHUB_TOKEN` is valid and not expired
- Check that token has appropriate scopes (`repo` or `public_repo`)
- Ensure `GITHUB_USERNAME` matches your GitHub username exactly

**Rate Limit Issues**
- Use the "Bypass Cache" checkbox sparingly
- Wait for rate limit reset (shown in error messages)
- Consider reducing the "Max Repositories for Charts" setting
- Use the cache controls to manage data freshness vs. API usage

**Empty Repository List**
- Check that your GitHub username is spelled correctly
- Verify your token has access to the repositories you expect
- Try the "Refresh" button to fetch fresh data
- Check the "Settings Help" panel in the sidebar for guidance

**Missing NEXT_STEPS Data**
- Ensure each repository has `comms/NEXT_STEPS.md` (preferred) or a legacy root-level `NEXT_STEPS.md`
- Files are processed based on the configurable "NEXT_STEPS Processing Limit" (10-100 repos)
- Repositories are prioritized by recent activity for processing
- Use repository filters to focus on specific projects

**Performance Issues**
- Reduce "Max Repositories for Charts" for faster loading
- Use cache controls to balance freshness vs. speed
- Filter repositories to focus on currently active projects

### Cache Controls

The dashboard includes intelligent caching to optimize performance:
- **Cache Stats**: View current cache status in the sidebar
- **Cache Telemetry**: See hits, misses, hit rate, and top cached functions for observability
- **Refresh Button**: Force refresh of repository list
- **Section Refresh**: Refresh just a section (Charts, NEXT_STEPS) without clearing the cache
- **Bypass Cache**: Temporarily disable all caching (use sparingly)
- **Clear Cache**: Remove all cached data and start fresh

## 📸 Screenshots

### Dashboard Overview
![Dashboard Overview](docs/screenshots/dashboard.png)
*Main dashboard showing repository statistics, filters, and data table*

### Visualizations
![Visualizations](docs/screenshots/visualizations.png)
*Interactive charts showing language distribution and commit activity*

### NEXT_STEPS Integration
![NEXT_STEPS Integration](docs/screenshots/next_steps.png)
*Task aggregation and repository-specific NEXT_STEPS display*
The dashboard looks for `comms/NEXT_STEPS.md` first (falling back to the legacy root `NEXT_STEPS.md`). See `docs/NEXT_STEPS.template.md` for a recommended file structure.

## 📋 Project Structure

The application follows a modular architecture:

```
github_dashboard/
├── app.py                 # Main Streamlit application
├── config/               # Configuration management
├── services/             # Core business logic
├── ui/                   # User interface modules
│   ├── branding.py       # App title/logo helpers
│   ├── charts.py         # Plotly chart renderers
│   ├── checklists.py     # NEXT_STEPS UI
│   ├── controls.py       # Sidebar controls and settings help
│   ├── headers.py        # Section header styles and renderer
│   ├── metrics.py        # Metric cards and progress circle
│   ├── notifications.py  # Errors, cache info, last-updated
│   └── styles.py         # Global CSS/JS injectors
├── models/               # Data models and types
├── docs/                 # Documentation and screenshots
├── comms/                # Development workflow management
└── requirements.txt      # Python dependencies
```

## 🗺️ Roadmap & Architecture

For detailed information about the project's architecture and future plans:

- [**Architecture Documentation**](docs/ARCHITECTURE.md) - System design and component interactions
- [**Development Roadmap**](docs/ROADMAP.md) - Feature timeline and implementation phases

## 🚢 Deploy

See the Deployment Guide for Streamlit Community Cloud and Docker instructions:
- [**Deployment Guide**](docs/DEPLOYMENT.md)

## 🤝 Contributing

This project uses a structured development workflow with separate Architect and Developer roles. See the `comms/` directory for task specifications and development logs.

## 📝 License

This project is open source and available under the MIT License.

## 🆘 Support

If you encounter issues:

1. Check the "Settings Help" panel in the application sidebar
2. Review the troubleshooting section above
3. Verify your `.env` configuration matches `.env.example`
4. Check that your GitHub token has the required permissions

For additional support, please refer to the project documentation or create an issue in the repository.
