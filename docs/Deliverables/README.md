# CQ Lite - AI-Powered Code Quality Analysis Tool

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104.0+-green.svg)](https://fastapi.tiangolo.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-0.2.0+-purple.svg)](https://github.com/langchain-ai/langgraph)

<img width="1024" height="1024" alt="image" src="https://github.com/user-attachments/assets/80cbfc6f-eef5-4578-b7ee-5bc5463558ec" />

CQ Lite is an intelligent, multi-agent code quality analysis tool that combines traditional static analysis with AI-powered insights. It provides comprehensive code reviews, security analysis, and quality metrics for Python, JavaScript, and Docker projects.

## 🚀 Key Features

### Multi-Modal Analysis
- **Python Analysis**: AST-based complexity analysis, security scanning with Bandit, hardcoded secrets detection
- **JavaScript Analysis**: Syntax validation, complexity metrics, best practices checking
- **Docker Analysis**: Dockerfile security scanning, optimization recommendations
- **GitHub Repository Analysis**: Direct analysis of remote repositories without cloning

### AI-Powered Intelligence
- **Multi-Agent Workflow**: Orchestrated using LangGraph for intelligent task routing
- **Hybrid Analysis**: Combines traditional static analysis with AI-enhanced insights
- **Token Optimization**: Smart truncation and description generation to reduce API costs by 20%+
- **Vector Database Integration**: Early population during analysis for enhanced Q&A capabilities

### Enterprise Features
- **Notion Integration**: Automated report publishing to Notion workspace
- **Interactive Q&A**: Chat with your codebase using vector-enhanced knowledge base
- **Multiple AI Models**: Support for Google Gemini and Nebius AI
- **FastAPI Server**: RESTful API for integration with CI/CD pipelines
- **CLI Interface**: Command-line tool for local and remote analysis

## 📦 Installation

### Prerequisites
- Python 3.9 or higher
- UV package manager (recommended) or pip

### Quick Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/cq-lite.git
   cd cq-lite
   ```

2. **Install dependencies**
   ```bash
   # Using UV (recommended)
   uv sync

   # Or using pip
   pip install -e .
   ```

3. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

### Environment Variables

Create a `.env` file with the following variables:

```bash
# AI Model APIs (choose at least one)
GOOGLE_API_KEY=your_google_api_key_here
NEBIUS_API_KEY=your_nebius_api_key_here

# GitHub Integration (for repository analysis)
GITHUB_API_TOKEN=your_github_token_here

# Notion Integration (optional)
NOTION_TOKEN=your_notion_integration_token
NOTION_PAGE_ID=your_notion_page_id

# OpenAI (for vector embeddings)
OPENAI_API_KEY=your_openai_api_key_here
```

**Get your API keys:**
- **Google AI**: https://makersuite.google.com/app/apikey
- **GitHub**: https://github.com/settings/tokens (needs repo access)
- **Notion**: https://www.notion.so/my-integrations
- **Nebius AI**: https://console.nebius.com/
- **OpenAI**: https://platform.openai.com/api-keys

## 🔧 Usage

### Command Line Interface

#### Basic Analysis
```bash
# Analyze local directory
uv run python -m cli.agentic_cli analyze /path/to/your/code

# Analyze GitHub repository
uv run python -m cli.agentic_cli analyze --repourl https://github.com/owner/repo

# Quick analysis with token optimization
uv run python -m cli.agentic_cli analyze --repourl https://github.com/owner/repo --quick --max-files 10
```

#### Advanced Options
```bash
# Full analysis with Notion reporting
uv run python -m cli.agentic_cli analyze \
  --repourl https://github.com/owner/repo \
  --model gemini \
  --notion \
  --max-files 20 \
  --severity high

# Interactive Q&A mode
uv run python -m cli.agentic_cli chat

# Check environment setup
uv run python -m cli.agentic_cli env
```

## 🏗️ Architecture Overview

CQ Lite uses a multi-agent architecture orchestrated by LangGraph:

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   CLI/API       │───▶│   Workflow       │───▶│   Agents        │
│   Interface     │    │   Orchestrator   │    │   - Discovery   │
└─────────────────┘    │   (LangGraph)    │    │   - Analysis    │
                       └──────────────────┘    │   - AI Review   │
                                │              │   - Q&A         │
                                │              │   - Notion      │
                                ▼              └─────────────────┘
                       ┌──────────────────┐
                       │   Vector Store   │
                       │   (ChromaDB)     │
                       └──────────────────┘
```

### Core Components

1. **File Discovery Agent**: Intelligently discovers and categorizes files
2. **Language-Specific Analyzers**: Python, JavaScript, Docker analysis
3. **AI Review Agent**: Comprehensive AI-powered code review
4. **Q&A Agent**: Interactive codebase exploration
5. **Notion Report Agent**: Automated documentation generation
6. **Vector Store**: ChromaDB for semantic code search

### Why LangGraph? A Design Decision Story

When building CQ Lite, I evaluated several frameworks for orchestrating the multi-agent workflow:

**Options Considered:**
- **CrewAI**: Great for predefined agent roles, but felt restrictive for custom workflows
- **OpenAI SDK**: Powerful for single-agent tasks, but lacking orchestration capabilities
- **Google AI SDK**: Excellent for Gemini integration, but no workflow management
- **LangChain**: Good foundation, but too heavyweight for our specific needs

**Why LangGraph Won:**
- **Complete Workflow Freedom**: I could design exactly the agent flow I envisioned - conditional routing, parallel execution, dynamic state management
- **Visual Workflow Design**: The graph-based approach made it easy to visualize and debug complex agent interactions
- **State Management**: Built-in state passing between agents without boilerplate code
- **Flexibility**: Could easily add new agents, modify routing logic, or change execution order without rewriting core logic
- **Performance**: Lightweight compared to full LangChain while keeping the power I needed

The breakthrough moment was realizing I could create conditional edges that route based on discovered files - something that would have been much harder to implement cleanly in other frameworks. LangGraph's philosophy of "graphs as code" aligned perfectly with my vision of an intelligent, adaptive analysis pipeline.

## 💡 Key Features Deep Dive

### Token Optimization Strategy
- **Smart Truncation**: Files with no quality issues and low interdependency are truncated with AI-generated descriptions
- **Token Savings**: Achieves 20%+ reduction in API token usage
- **Context Preservation**: Maintains code understanding while reducing costs

### Vector Database Integration
- **Early Population**: Vector store is populated during analysis, not after
- **Enhanced Q&A**: Enables semantic search across the entire codebase
- **Persistent Knowledge**: Analysis results are stored for future queries

### Hybrid Analysis Approach
- **Traditional + AI**: Combines AST analysis, security scanning, and AI insights
- **Issue Enhancement**: AI enhances traditional static analysis findings
- **Contextual Understanding**: AI provides business impact and architectural insights

## 📊 Example Output

### Analysis Report
```
📊 Analysis Summary for my-project/
├── 📁 Files Analyzed: 25
├── 🐍 Python Files: 15 (600 lines)
├── 🟨 JavaScript Files: 8 (450 lines)
├── 🐳 Docker Files: 2
└── ⚠️  Issues Found: 12

🔍 Key Issues:
├── 🔴 Critical: Hardcoded API key in config.py:15
├── 🟠 High: Complex function in main.py:45 (CC: 12)
└── 🟡 Medium: Missing error handling in api.py:23

🤖 AI Insights:
├── Business Impact: High - Security vulnerabilities detected
├── Architecture: Consider implementing dependency injection
└── Priority: Address security issues immediately
```

### Notion Integration
Reports are automatically published to Notion with:
- Executive summary and metrics
- Detailed issue breakdown with severity
- Fix recommendations and priority matrix
- Code snippets and architectural insights

## 🛠️ Development

### Project Structure
```
cq-lite/
├── api/                 # FastAPI server
│   ├── models/         # Pydantic models
│   ├── routers/        # API endpoints
│   └── services/       # Business logic
├── backend/            # Core analysis engine
│   ├── agents/         # LangGraph agents
│   ├── analyzers/      # Language-specific analyzers
│   ├── models/         # Data models
│   ├── services/       # AI services
│   └── tools/          # Integration tools
├── cli/                # Command-line interface
├── frontend/           # Next.js frontend
├── docs/               # Documentation
└── tests/              # Test suites
```

### Running Tests
```bash
# Run all tests
uv run pytest

# Run specific test suite
uv run pytest tests_server/
uv run pytest test_cli/
```

## 🔗 API Reference

### Core Endpoints

#### GitHub Analysis
```http
POST /api/github/analyze
Content-Type: application/json

{
  "repo_url": "https://github.com/owner/repo",
  "model_choice": "gemini",
  "max_files": 10,
  "severity_filter": "medium"
}
```

#### File Upload Analysis
```http
POST /api/upload
Content-Type: multipart/form-data

files: [file1.py, file2.js, ...]
model_choice: "gemini"
```

#### Analysis Status
```http
GET /api/status/{job_id}
```

#### Q&A Interface
```http
POST /api/chat
Content-Type: application/json

{
  "query": "What are the main security issues in this codebase?",
  "context": "analysis_results"
}
```

## 🚀 Deployment

### Docker Deployment
```bash
# Build and run
docker build -t cq-lite .
docker run -p 8000:8000 --env-file .env cq-lite
```

### Cloud Deployment
- **Render**: Uses `render.yaml` configuration
- **Netlify**: Frontend deployment with `netlify.toml`
- **Vercel**: Next.js frontend deployment

## 🧪 Testing

### CLI Testing
```bash
# Test analysis on sample repository
uv run python -m cli.agentic_cli analyze --repourl https://github.com/python/cpython --max-files 5 --quick

# Test Q&A functionality
uv run python -m cli.agentic_cli chat
```

### API Testing
```bash
# Start server
uv run python -m api

# Test in another terminal
curl -X GET http://localhost:8000/api/health
```

## 📝 Troubleshooting

### Common Issues

1. **Missing API Keys**
   ```bash
   uv run python -m cli.agentic_cli env
   ```

2. **Token Limit Exceeded**
   - Use `--quick` flag for faster analysis
   - Reduce `--max-files` parameter
   - Enable smart truncation (default)

3. **Vector Store Issues**
   ```bash
   # Clear vector database
   rm -rf db/chroma_db/
   ```

4. **GitHub Rate Limits**
   - Ensure `GITHUB_API_TOKEN` is set
   - Reduce analysis scope with `--max-files`
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
uv run python -m cli.agentic_cli analyze ./src

# Filter by severity
uv run python -m cli.agentic_cli analyze ./src --severity high

# Get detailed resolution steps for each issue
uv run python -m cli.agentic_cli analyze ./src --insights

# JSON output
uv run python -m cli.agentic_cli analyze ./src --format json
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

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🤝 Support

- **Issues**: [GitHub Issues](https://github.com/yourusername/cq-lite/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/cq-lite/discussions)
- **Documentation**: [docs/](docs/)

## � Acknowledgments

- **LangGraph**: Multi-agent orchestration framework
- **FastAPI**: High-performance web framework
- **ChromaDB**: Vector database for semantic search
- **Radon**: Python complexity analysis
- **Bandit**: Python security analysis
- **Notion API**: Documentation integration

---

Built with ❤️ using AI-powered architecture and modern Python frameworks.
