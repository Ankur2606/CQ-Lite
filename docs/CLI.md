# CQ Lite CLI Documentation

This document provides comprehensive documentation for the CQ Lite command-line interface.

## Overview

The CQ Lite CLI offers powerful tools for analyzing code quality, security vulnerabilities, and maintainability. It supports both local file analysis and GitHub repository analysis.

## Requirements

- Python 3.11+
- uv package manager
- Required API keys (see [Environment Setup](#environment-setup))

## Environment Setup

Before using the CLI, you need to set up your environment variables. Create a `.env` file in the project root with the following variables:

```bash
# Required for AI analysis - Choose one or both
GOOGLE_API_KEY=your-gemini-api-key     # Required for Gemini AI analysis
NEBIUS_API_KEY=your-nebius-key         # Alternative AI model

# Required for GitHub repository analysis
GITHUB_API_TOKEN=your-github-token     # Required for GitHub repository analysis

# Optional: Required only for Notion integration
NOTION_TOKEN=your-notion-token         # Optional: For Notion integration
NOTION_PAGE_ID=your-notion-page-id     # Optional: For Notion integration
```

You can check your environment setup with:

```bash
uv run python -m cli env
```

## Command Structure

The CLI has several main commands:

```
cli
├── analyze     # Code analysis with detailed reports
├── review      # Generate comprehensive code reviews
├── chat        # Interactive Q&A about your codebase
└── env         # Display environment variable status
```

## Commands

### Analyze Command

The `analyze` command performs code analysis on local files or GitHub repositories.

```bash
uv run python -m cli analyze [PATH] [OPTIONS]
```

#### Arguments:

- `PATH`: Path to the directory or file to analyze (required if `--repourl` is not provided)

#### Options:

- `--repourl, -r TEXT`: GitHub repository URL to analyze
- `--format, -f [text|json]`: Output format (default: text)
- `--severity, -s [low|medium|high|critical]`: Filter by severity
- `--insights, -i`: Generate AI insights
- `--model [gemini|nebius]`: Choose the AI model for analysis (default: gemini)
- `--quick`: Run a quick analysis, skipping vector store and using Nebius model
- `--notion`: Push analysis results to Notion (requires NOTION_TOKEN and NOTION_PAGE_ID env vars)
- `--max-files INTEGER`: Maximum number of files to analyze when using --repourl (default: 100)

#### Examples:

```bash
# Analyze local directory
uv run python -m cli analyze ./src

# Analyze GitHub repository
uv run python -m cli analyze --repourl https://github.com/username/repo

# Filter by severity
uv run python -m cli analyze ./src --severity high

# Get JSON output
uv run python -m cli analyze ./src --format json

# Generate AI insights
uv run python -m cli analyze ./src --insights

# Use specific AI model
uv run python -m cli analyze ./src --model nebius

# Run quick analysis
uv run python -m cli analyze ./src --quick

# Push results to Notion
uv run python -m cli analyze ./src --notion
```

### Review Command

The `review` command generates comprehensive code reviews with analysis and recommendations.

```bash
uv run python -m cli review [PATH] [OPTIONS]
```

#### Arguments:

- `PATH`: Path to the directory or file to review (required if `--repourl` is not provided)

#### Options:

- `--repourl, -r TEXT`: GitHub repository URL to analyze
- `--format, -f [text|json|md|html|notion]`: Output format (default: text)
- `--service [gemini|nebius]`: AI service to use for report generation (default: gemini)
- `--notion`: Push comprehensive report to Notion (requires NOTION_TOKEN and NOTION_PAGE_ID env vars)
- `--max-files INTEGER`: Maximum number of files to analyze when using --repourl (default: 100)

#### Examples:

```bash
# Review local directory
uv run python -m cli review ./src

# Review GitHub repository
uv run python -m cli review --repourl https://github.com/username/repo

# Get markdown output
uv run python -m cli review ./src --format md

# Use specific AI service
uv run python -m cli review ./src --service nebius

# Push review to Notion
uv run python -m cli review ./src --notion
```

### Chat Command

The `chat` command provides interactive Q&A about your codebase.

```bash
uv run python -m cli chat [OPTIONS]
```

#### Options:

- `--context, -c PATH`: Path to analyzed code for context
- `--notion`: Push analysis results to Notion when analysis is triggered (requires NOTION_TOKEN and NOTION_PAGE_ID env vars)

#### Examples:

```bash
# Start chat with default context
uv run python -m cli chat

# Start chat with specific context
uv run python -m cli chat --context ./src

# Enable Notion integration
uv run python -m cli chat --notion
```

#### Chat Commands:

Inside the chat mode, you can use the following commands:

- `analyze PATH`: Trigger code analysis for the specified path
- `review PATH`: Generate a comprehensive review for the specified path
- `exit`, `quit`, `bye`: Exit the chat mode

### Env Command

The `env` command displays environment variable status and setup instructions.

```bash
uv run python -m cli env
```

This command shows the status of all required environment variables and provides setup instructions for any missing variables.

## Agentic CLI

The project also includes an advanced "agentic" CLI that uses AI agents for more intelligent analysis.

```bash
uv run python -m cli.agentic_cli [COMMAND] [OPTIONS]
```

### Agentic Analyze Command

```bash
uv run python -m cli.agentic_cli analyze [PATH] [OPTIONS]
```

Options are similar to the standard analyze command, but with AI-orchestrated analysis.

### Agentic Review Command

```bash
uv run python -m cli.agentic_cli review [PATH] [OPTIONS]
```

Options are similar to the standard review command, but with AI-driven comprehensive reviews.

### Agentic Chat Command

```bash
uv run python -m cli.agentic_cli chat [OPTIONS]
```

Provides an enhanced chat experience with AI agents that can trigger analysis workflows.

## Error Messages and Troubleshooting

### Missing Environment Variables

If environment variables are missing, the CLI will display helpful messages:

```
❌ Missing required environment variables.

Please set the following environment variables:

  GOOGLE_API_KEY:
    Purpose: Gemini API access for AI analysis
    Command: $env:GOOGLE_API_KEY="your-google_api_key-here"
    More info: https://ai.google.dev/tutorials/setup

Or add to your .env file in the project root:

GOOGLE_API_KEY=your-google_api_key-here

For more information, please refer to: https://github.com/Ankur2606/CQ-Lite/blob/master/README.md
```

### Common Issues

1. **GitHub API Rate Limits**: Without a GitHub token, you may hit rate limits. Use `GITHUB_API_TOKEN` to avoid this.
2. **Analysis Failures**: If analysis fails, check that you have the correct AI service API keys set up.
3. **Large Repository Analysis**: For very large repositories, use the `--max-files` option to limit the number of files analyzed.

## Best Practices

1. **Set Up Environment Variables**: Always configure all required API keys before using the CLI.
2. **Use Severity Filtering**: For large codebases, filter by severity to focus on critical issues first.
3. **AI Insights**: Enable `--insights` to get detailed AI explanations and fix suggestions.
4. **Use Quick Analysis**: For initial assessments, use the `--quick` flag to speed up analysis.
5. **Notion Integration**: For team collaboration, use the Notion integration to share results.

## Output Formats

The CLI supports multiple output formats:

- **text**: Rich formatted text for terminal display
- **json**: Structured data for programmatic processing
- **md**: Markdown format for documentation
- **html**: HTML format for web display
- **notion**: Directly push to Notion (requires credentials)

## Advanced Usage

### Docker Analysis

The tool includes specialized analyzers for Docker files:

```bash
uv run python -m cli analyze --repourl https://github.com/username/docker-project
```

This will automatically detect and analyze Docker files for best practices and security issues.

### Integration with CI/CD

You can integrate the CLI into your CI/CD pipelines:

```yaml
# Example GitHub Action
- name: Analyze code quality
  run: |
    pip install uv
    uv sync
    uv run python -m cli analyze . --format json --severity high
```

## Further Resources

- [Setup Guide](docs/SETUP.md): Detailed setup instructions
- [Architecture Documentation](docs/ARCHITECTURE.md): Technical architecture details
- [Demo Examples](docs/DEMO.md): Example use cases and outputs