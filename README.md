# Code Quality Intelligence Agent

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

### CLI Usage
```bash
# Analyze code
uv run python -m cli analyze ./src

# Start interactive chat
uv run python -m cli chat
```

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

**Analyze Code**:
```bash
# Analyze a directory
uv run python -m cli analyze ./src

# Filter by severity
uv run python -m cli analyze ./src --severity high

# Get detailed resolution steps for each issue
uv run python -m cli analyze ./src --insights

# Combine filters with insights
uv run python -m cli analyze ./src --severity high --insights

# JSON output
uv run python -m cli analyze ./src --format json
```

**Interactive Chat**:
```bash
# Start chat session
uv run python -m cli chat

# Chat with code context
uv run python -m cli chat --context ./src
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

✅ **AI Integration**
- Gemini-powered conversational interface
- Context-aware code explanations
- Actionable improvement suggestions

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