# Architecture Overview

## System Design

The Code Quality Intelligence Agent is built with a modern, scalable architecture that separates concerns between analysis, AI processing, and user interfaces.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Frontend      │    │   Backend       │    │   AI Services   │
│   (Next.js)     │◄──►│   (FastAPI)     │◄──►│   (Gemini)      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                              │
                              ▼
                       ┌─────────────────┐
                       │   Analyzers     │
                       │   (AST-based)   │
                       └─────────────────┘
```

## Components

### Backend (Python FastAPI)
- **Main API Server**: Handles HTTP requests, file uploads, and orchestrates analysis
- **Code Analyzers**: AST-based analysis for Python and JavaScript
- **Gemini Service**: AI-powered chat and insights
- **Models**: Pydantic models for type safety and validation

### Frontend (Next.js)
- **Landing Page**: File upload and feature showcase
- **Dashboard**: Visual analysis results with filtering
- **Chat Interface**: Conversational AI about codebase
- **Dark Gradient Theme**: Modern, accessible UI design

### CLI Interface
- **Analysis Command**: `analyze <path>` for code analysis
- **Chat Command**: `chat` for interactive Q&A
- **Rich Formatting**: Beautiful terminal output

### Analyzers

#### Python Analyzer
- **AST Parsing**: Uses Python's `ast` module
- **Complexity**: Radon for cyclomatic complexity
- **Security**: Bandit for vulnerability detection
- **Performance**: Custom heuristics for bottlenecks

#### JavaScript Analyzer
- **Syntax Analysis**: Basic parsing and structure analysis
- **Performance**: DOM query optimization detection
- **Security**: Pattern matching for unsafe practices
- **Quality**: Function length and complexity estimation

## Data Flow

1. **Code Input**: Files uploaded via web UI or analyzed via CLI
2. **Language Detection**: File extensions determine analyzer
3. **AST Analysis**: Code parsed into abstract syntax trees
4. **Issue Detection**: Multiple analyzers scan for problems
5. **Report Generation**: Results formatted for display
6. **AI Enhancement**: Gemini provides contextual insights

## Key Features

### AST-Based Analysis
- Deep structural understanding of code
- Accurate complexity measurements
- Precise duplication detection
- Security vulnerability identification

### Multi-Language Support
- Python: Full AST analysis with radon/bandit
- JavaScript/TypeScript: Syntax and pattern analysis
- Extensible architecture for additional languages

### AI Integration
- Contextual code understanding
- Natural language explanations
- Actionable improvement suggestions
- Conversational interface

### Modern UI/UX
- Dark gradient theme with accessibility
- Responsive design for all devices
- Interactive visualizations
- Real-time chat interface

## Technology Stack

- **Backend**: Python 3.11+, FastAPI, uvicorn, uv
- **Frontend**: Next.js 14, React 18, Tailwind CSS
- **AI**: Google Gemini Pro, Langgraph
- **Analysis**: AST, Radon, Bandit, Esprima
- **CLI**: Click, Rich for beautiful terminal output