# CQ Lite Setup Guide

## Prerequisites

- **Python 3.9 or higher** (tested with Python 3.11+)
- **Node.js 18 or higher** (for frontend development)
- **UV package manager** (for dependency management)
- **Git** (for repository cloning)

## Quick Start (Recommended)

### 1. Clone and Install

```bash
git clone https://github.com/Ankur2606/CQ-Lite.git
cd CQ-Lite
```

### 2. Install UV Package Manager

```bash
# On Windows (PowerShell)
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# On macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# Alternative: via pip
pip install uv
```

### 3. Install Dependencies

```bash
# Install all Python dependencies using UV
uv sync

# This will create a virtual environment and install all dependencies
# from pyproject.toml including FastAPI, LangGraph, ChromaDB, etc.
```

### 4. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env with your API keys (see Environment Variables section below)
```

### 5. Verify Installation

```bash
# Check if everything is set up correctly
uv run python -m cli.agentic_cli env

# You should see a status report of your environment setup
```

## Environment Variables

CQ Lite requires several API keys for full functionality. Copy `.env.example` to `.env` and configure:

### Required Variables

```bash
# AI Model APIs (at least one required)
GOOGLE_API_KEY=your-gemini-api-key-here
NEBIUS_API_KEY=your-nebius-api-key-here

# GitHub Integration (required for repository analysis)
GITHUB_API_TOKEN=your-github-personal-access-token-here
```

### Optional Variables

```bash
# Notion Integration (for automated report publishing)
NOTION_TOKEN=your-notion-integration-token-here
NOTION_PAGE_ID=your-notion-page-id-here

# OpenAI (for vector embeddings - uses Nebius if not set)
OPENAI_API_KEY=your-openai-api-key-here
```

### Getting API Keys

1. **Google Gemini API**: 
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create new API key
   - Copy to your `.env` file

2. **GitHub Token**:
   - Go to [GitHub Personal Access Tokens](https://github.com/settings/tokens)
   - Generate new token with `repo` scope
   - Copy to your `.env` file

3. **Nebius AI** (optional):
   - Visit [Nebius Console](https://console.nebius.com/)
   - Generate API key
   - Copy to your `.env` file

4. **Notion Integration** (optional):
   - Go to [Notion Integrations](https://www.notion.so/my-integrations)
   - Create new integration
   - Copy integration token and page ID

## Running CQ Lite

### CLI Usage (Primary Interface)

```bash
# Analyze local directory
uv run python -m cli.agentic_cli analyze /path/to/your/code

# Analyze GitHub repository
uv run python -m cli.agentic_cli analyze --repourl https://github.com/owner/repo

# Quick analysis (faster, limited files)
uv run python -m cli.agentic_cli analyze --repourl https://github.com/owner/repo --quick --max-files 10

# Interactive Q&A with your codebase
uv run python -m cli.agentic_cli chat

# Check environment setup
uv run python -m cli.agentic_cli env
```

### API Server (Web Interface)

```bash
# Start the FastAPI backend server
uv run python -m api

# Server will be available at http://localhost:8000
# API documentation at http://localhost:8000/docs
```

### Frontend Development (Optional)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Start development server
npm run dev

# Frontend will be available at http://localhost:3000
```

## Usage Examples

### Basic Analysis

```bash
# Analyze current directory
uv run python -m cli.agentic_cli analyze .

# Analyze specific directory
uv run python -m cli.agentic_cli analyze /path/to/project

# Analyze with specific model
uv run python -m cli.agentic_cli analyze . --model gemini

# Filter by severity
uv run python -m cli.agentic_cli analyze . --severity high
```

### GitHub Repository Analysis

```bash
# Full repository analysis
uv run python -m cli.agentic_cli analyze --repourl https://github.com/microsoft/vscode

# Quick analysis for large repos
uv run python -m cli.agentic_cli analyze --repourl https://github.com/microsoft/vscode --quick --max-files 15

# With Notion reporting
uv run python -m cli.agentic_cli analyze --repourl https://github.com/owner/repo --notion
```

### Interactive Features

```bash
# Start Q&A session
uv run python -m cli.agentic_cli chat

# Q&A with specific project context
uv run python -m cli.agentic_cli chat --context /path/to/project
```

## API Endpoints

When running the API server (`uv run python -m api`):

- **POST** `/api/github/analyze` - Analyze GitHub repository
- **POST** `/api/upload` - Upload files for analysis  
- **POST** `/api/chat` - Interactive Q&A with codebase
- **GET** `/api/status/{job_id}` - Check analysis status
- **GET** `/api/health` - Health check
- **GET** `/docs` - Interactive API documentation

## Project Structure

```
CQ-Lite/
├── api/                 # FastAPI web server
│   ├── main.py         # API entry point
│   ├── routers/        # API route handlers
│   └── models/         # API data models
├── backend/            # Core analysis engine
│   ├── agents/         # LangGraph agents
│   ├── analyzers/      # Language-specific analyzers
│   ├── services/       # AI and external services
│   └── tools/          # Integration tools
├── cli/                # Command-line interface
│   ├── agentic_cli.py  # Main CLI entry point
│   └── env_helpers.py  # Environment validation
├── frontend/           # Next.js web interface
├── docs/               # Documentation
└── tests/              # Test suites
```

## Troubleshooting

### Common Installation Issues

1. **"uv not found" or "command not found"**:
   ```bash
   # Ensure UV is installed and in PATH
   pip install uv
   
   # Or reinstall UV
   curl -LsSf https://astral.sh/uv/install.sh | sh
   
   # On Windows PowerShell
   powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
   ```

2. **"uv install failed" or dependency conflicts**:
   ```bash
   # Clear UV cache and reinstall
   uv cache clean
   uv sync --no-cache
   
   # If that fails, remove lock file and try again
   rm uv.lock
   uv sync
   ```

3. **"GOOGLE_API_KEY not set" error**:
   ```bash
   # Check your .env file exists and has the correct key
   cat .env | grep GOOGLE_API_KEY
   
   # Verify environment setup
   uv run python -m cli.agentic_cli env
   ```

4. **"ModuleNotFoundError" when running CLI**:
   ```bash
   # Ensure you're using UV to run commands
   uv run python -m cli.agentic_cli --help
   
   # Don't use: python -m cli.agentic_cli
   # Always use: uv run python -m cli.agentic_cli
   ```

### API/Server Issues

1. **Port already in use**:
   ```bash
   # Kill process using port 8000
   # On Windows
   netstat -ano | findstr :8000
   taskkill /PID <process_id> /F
   
   # On macOS/Linux
   lsof -ti:8000 | xargs kill -9
   
   # Or use different port
   uv run python -m api --port 8001
   ```

2. **CORS errors in frontend**:
   ```bash
   # Ensure backend is running on http://localhost:8000
   # Frontend expects backend on this exact URL
   ```

### Analysis Issues

1. **"Rate limit exceeded" for GitHub**:
   - Ensure `GITHUB_API_TOKEN` is set in `.env`
   - Use `--max-files` to limit analysis scope
   - Wait and retry (GitHub rate limits reset hourly)

2. **"Token limit exceeded" for AI models**:
   ```bash
   # Use quick mode for large repositories
   uv run python -m cli.agentic_cli analyze --repourl <url> --quick --max-files 10
   
   # Or analyze specific directories instead of entire repo
   uv run python -m cli.agentic_cli analyze /path/to/specific/directory
   ```

3. **ChromaDB/Vector store errors**:
   ```bash
   # Clear vector database
   rm -rf db/chroma_db
   
   # It will be recreated on next analysis
   ```

### Performance Optimization

1. **Slow analysis on large codebases**:
   - Use `--quick` flag for faster analysis
   - Limit files with `--max-files N`
   - Analyze specific directories instead of entire repository
   - Use `--severity high` to focus on critical issues

2. **High memory usage**:
   - Reduce `--max-files` limit
   - Analyze in smaller batches
   - Close other applications to free memory

## Development Setup

### Running Tests

```bash
# Run all Python tests
uv run pytest

# Run specific test files
uv run pytest test_cli/
uv run pytest tests_server/

# Run with coverage
uv run pytest --cov=backend --cov=cli
```

### Code Quality

```bash
# Format Python code
uv run black .
uv run isort .

# Type checking
uv run mypy backend/ cli/

# Frontend linting
cd frontend
npm run lint
```

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make changes and add tests
4. Run tests: `uv run pytest`
5. Format code: `uv run black . && uv run isort .`
6. Commit and push changes
7. Create a pull request

## Additional Resources

- **Documentation**: See `docs/` directory for detailed guides
- **CLI Reference**: [CLI.md](CLI.md) for complete command documentation
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md) for system design
- **Technical Details**: [TECHNICAL_NOTES.md](TECHNICAL_NOTES.md) for implementation details
- **Issues**: Report bugs and request features on GitHub
- **Discussions**: Join community discussions on GitHub Discussions

## System Requirements

**Minimum:**
- Python 3.9+
- 4GB RAM
- 1GB free disk space

**Recommended:**
- Python 3.11+
- 8GB+ RAM (for large codebases)
- 2GB+ free disk space
- SSD for faster analysis