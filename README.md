# Code Quality Intelligence Agent

<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/80cbfc6f-eef5-4578-b7ee-5bc5463558ec" />

An AI-powered code analysis tool that provides deep insights into code quality, security, and maintainability using AST-based analytics and Gemini AI.

## Features

- **AST-Based Analysis**: Deep structural analysis for Python and JavaScript
- **Multi-Category Detection**: Security, performance, duplication, complexity issues
- **AI-Powered Q&A**: Interactive chat about your codebase using Gemini
- **Dual Interface**: CLI commands and modern web UI
- **Developer-Friendly Reports**: Actionable insights with fix suggestions

## Tech Stack

- **Backend**: Python (FastAPI + uvicorn), managed with uv
- **Frontend**: Next.js + React + Tailwind CSS
- **AI**: Gemini via Langgraph
- **Analysis**: AST parsing, complexity metrics, security scanning

## Quick Start

### Backend Setup
```bash
# Install uv (Python package manager)
pip install uv

# Install dependencies
uv sync

# Start the server
uv run uvicorn app.main:app --reload
```

### Frontend Setup
```bash
cd frontend
npm install
npm run dev
```

### Environment Setup

This tool requires various API keys for different features:

```bash
# Create a .env file in the project root with the following variables:
GOOGLE_API_KEY=your-gemini-api-key     # Required for Gemini AI analysis
GITHUB_API_TOKEN=your-github-token     # Required for GitHub repository analysis
NEBIUS_API_KEY=your-nebius-key         # Optional: Alternative AI model
NOTION_TOKEN=your-notion-token         # Optional: For Notion integration
NOTION_PAGE_ID=your-notion-page-id     # Optional: For Notion integration
```

You can check your environment setup with:
```bash
uv run python -m cli env
```

### CLI Usage
```bash
# Analyze code
uv run python -m cli analyze ./src

# Analyze GitHub repository
uv run python -m cli analyze --repourl https://github.com/username/repo

# Generate comprehensive review
uv run python -m cli review ./src

# Start interactive chat
uv run python -m cli chat
```

See [docs/CLI.md](docs/CLI.md) for comprehensive CLI documentation.

## Project Structure

```
├── backend/           # Python FastAPI backend
├── frontend/          # Next.js web interface
├── cli/              # Command-line interface
├── analyzers/        # AST-based code analyzers
└── docs/             # Documentation
```

## Installation

### Automated Setup
```bash
python setup.py
```

### Manual Setup

1. **Backend Setup**:
   ```bash
   # Install uv (Python package manager)
   pip install uv
   
   # Install dependencies
   uv sync
   
   # Configure environment
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

2. **Frontend Setup**:
   ```bash
   cd frontend
   npm install
   ```

3. **Get Gemini API Key**:
   - Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
   - Create an API key
   - Add to your `.env` file

## Usage

### Start the Services

**Backend**:
```bash
uv run uvicorn backend.main:app --reload
```

**Frontend**:
```bash
cd frontend
npm run dev
```

### CLI Commands

**Traditional Analysis**:
```bash
# Analyze a directory
uv run python -m cli analyze ./src

# Filter by severity
uv run python -m cli analyze ./src --severity high

# Get detailed resolution steps for each issue
uv run python -m cli analyze ./src --insights

# JSON output
uv run python -m cli analyze ./src --format json
```

**🤖 NEW: Agentic Analysis (LangGraph-powered)**:
```bash
# AI-orchestrated analysis with intelligent agents
uv run python -m cli.agentic_cli analyze ./src

# Agentic analysis with AI insights
uv run python -m cli.agentic_cli analyze ./src --insights

# AI agents determine optimal analysis strategy
uv run python -m cli.agentic_cli analyze ./src --severity high
```
**Agent Architecture Diagram**:
--
<img width="1393" height="3840" alt="Untitled diagram _ Mermaid Chart-2025-09-16-231002" src="https://github.com/user-attachments/assets/f6dc4ac7-3057-4910-9022-e3169fa9e171" />


**Interactive Chat**:
```bash
# Traditional chat
uv run python -m cli chat --context ./src

# Agentic chat (coming soon)
uv run python -m cli.agentic_cli chat --context ./src
```

### Web Interface

- **Landing**: http://localhost:3000 - Upload and analyze files
- **Dashboard**: http://localhost:3000/dashboard - View detailed results
- **Chat**: http://localhost:3000/chat - AI-powered Q&A

## Features Implemented

✅ **AST-Based Analysis**
- Python: Full AST parsing with complexity and security analysis
- JavaScript: Syntax analysis and pattern detection

✅ **Issue Detection**
- Security vulnerabilities (bandit integration)
- Performance bottlenecks
- Code complexity (cyclomatic complexity)
- Code duplication detection
- Style and quality issues
- Hardcoded secrets detection

✅ **AI Integration**
- Gemini-powered conversational interface
- Context-aware code explanations
- Actionable improvement suggestions
- **🆕 LangGraph Agentic Workflows**

✅ **🤖 Agentic System (NEW)**
- **AI-Orchestrated Analysis**: LangGraph agents coordinate analysis
- **Intelligent Strategy Planning**: AI determines optimal analysis approach
- **Multi-Agent Coordination**: Specialized agents for different languages
- **Dynamic Workflow Routing**: Conditional logic based on codebase structure

✅ **Modern Web UI**
- Dark gradient theme with accessibility
- Interactive dashboard with filtering
- Real-time chat interface
- Responsive design

✅ **CLI Interface**
- Rich terminal output
- Multiple output formats
- Severity filtering
- Interactive chat mode
- **🆕 Agentic CLI**: AI-powered analysis orchestration

## Architecture

The system uses a modern, scalable architecture:

- **Backend**: Python FastAPI with uvicorn
- **Frontend**: Next.js with Tailwind CSS
- **AI**: Google Gemini Pro via Langgraph
- **Analysis**: AST-based with radon, bandit
- **CLI**: Click with Rich formatting

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for detailed information.

## Demo

See [docs/DEMO.md](docs/DEMO.md) for a complete demo script and sample code.

## Development Status

🚀 **Ready for Use** - Core features implemented and tested
