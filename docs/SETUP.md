# Setup Guide

## Prerequisites

- Python 3.11 or higher
- Node.js 18 or higher
- Google Gemini API key

## Quick Start

1. **Clone and setup**:
   ```bash
   git clone <repository-url>
   cd code-quality-agent
   python setup.py
   ```

2. **Configure environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your GOOGLE_API_KEY
   ```

3. **Start the backend**:
   ```bash
   uv run uvicorn backend.main:app --reload
   ```

4. **Start the frontend**:
   ```bash
   cd frontend
   npm run dev
   ```

## Manual Setup

### Backend Setup

1. **Install uv** (Python package manager):
   ```bash
   pip install uv
   ```

2. **Install dependencies**:
   ```bash
   uv sync
   ```

3. **Install additional tools**:
   ```bash
   # For security analysis
   pip install bandit
   
   # For complexity analysis
   pip install radon
   ```

4. **Environment configuration**:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and set:
   - `GOOGLE_API_KEY`: Your Gemini API key
   - `HOST`: Server host (default: localhost)
   - `PORT`: Server port (default: 8000)

### Frontend Setup

1. **Navigate to frontend**:
   ```bash
   cd frontend
   ```

2. **Install dependencies**:
   ```bash
   npm install
   ```

3. **Start development server**:
   ```bash
   npm run dev
   ```

## Getting Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key
3. Copy the key to your `.env` file

## CLI Usage

### Analyze Code
```bash
# Analyze a directory
uv run python -m cli analyze ./src

# Analyze with specific severity filter
uv run python -m cli analyze ./src --severity high

# Output as JSON
uv run python -m cli analyze ./src --format json
```

### Interactive Chat
```bash
# Start chat session
uv run python -m cli chat

# Chat with code context
uv run python -m cli chat --context ./src
```

## Web Interface

1. **Landing Page**: http://localhost:3000
   - Upload files for analysis
   - Feature overview

2. **Dashboard**: http://localhost:3000/dashboard
   - View analysis results
   - Filter by severity/category
   - Detailed issue information

3. **Chat**: http://localhost:3000/chat
   - AI-powered Q&A about your code
   - Contextual suggestions

## API Endpoints

- `POST /api/analyze`: Analyze code at path
- `POST /api/upload`: Upload files for analysis
- `POST /api/chat`: Chat with AI about code
- `GET /api/health`: Health check

## Troubleshooting

### Common Issues

1. **"uv not found"**:
   ```bash
   pip install uv
   ```

2. **"GOOGLE_API_KEY not set"**:
   - Check your `.env` file
   - Ensure the key is valid

3. **"bandit not found"**:
   ```bash
   pip install bandit
   ```

4. **Frontend build errors**:
   ```bash
   cd frontend
   rm -rf node_modules package-lock.json
   npm install
   ```

### Performance Tips

- For large codebases, consider analyzing specific directories
- Use severity filters to focus on critical issues
- The CLI is faster for batch analysis

## Development

### Running Tests
```bash
# Backend tests
uv run pytest

# Frontend tests
cd frontend
npm test
```

### Code Formatting
```bash
# Python
uv run black .
uv run isort .

# TypeScript
cd frontend
npm run lint
```