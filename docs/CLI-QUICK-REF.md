# CLI Quick Reference Guide

## NAME
`cli` - CQ Lite CLI

## SYNOPSIS
```
uv run python -m cli [COMMAND] [ARGUMENTS...] [OPTIONS...]
```

## COMMANDS

### analyze
Perform code analysis on a directory or GitHub repository.

```
uv run python -m cli analyze [PATH] [OPTIONS]
  --repourl, -r TEXT                  GitHub repository URL to analyze
  --format, -f [text|json]            Output format (default: text)
  --severity, -s [low|medium|high|critical]
                                      Filter by severity
  --insights, -i                      Generate AI insights
  --model [gemini|nebius]             Choose the AI model for analysis
  --quick                             Run a quick analysis
  --notion                            Push analysis results to Notion
  --max-files INTEGER                 Maximum number of files to analyze (default: 100)
```

### review
Generate comprehensive code review with analysis and recommendations.

```
uv run python -m cli review [PATH] [OPTIONS]
  --repourl, -r TEXT                  GitHub repository URL to analyze
  --format, -f [text|json|md|html|notion]
                                      Output format (default: text)
  --service [gemini|nebius]           AI service to use (default: gemini)
  --notion                            Push report to Notion
  --max-files INTEGER                 Maximum number of files to analyze (default: 100)
```

### chat
Interactive Q&A using agentic workflow with analysis triggering.

```
uv run python -m cli chat [OPTIONS]
  --context, -c PATH                  Path to analyzed code for context
  --notion                            Push analysis results to Notion
```

### env
Show information about required environment variables.

```
uv run python -m cli env
```

## AGENTIC CLI

Enhanced AI-powered version of the CLI.

```
uv run python -m cli.agentic_cli [COMMAND] [ARGUMENTS...] [OPTIONS...]
```

Commands match the regular CLI with enhanced AI capabilities.

## ENVIRONMENT VARIABLES

- `GOOGLE_API_KEY` - Required for Gemini AI analysis
- `GITHUB_API_TOKEN` - Required for GitHub repository analysis
- `NEBIUS_API_KEY` - Alternative AI model for analysis
- `NOTION_TOKEN` - Required for Notion integration
- `NOTION_PAGE_ID` - Required for Notion integration

## EXAMPLES

```bash
# Basic code analysis
uv run python -m cli analyze ./src

# Analyze GitHub repo with detailed insights
uv run python -m cli analyze --repourl https://github.com/username/repo --insights

# Generate a comprehensive review
uv run python -m cli review ./src --format md

# Start an interactive chat session
uv run python -m cli chat --context ./src

# Check environment variable status
uv run python -m cli env

# Use the agentic workflow for analysis
uv run python -m cli.agentic_cli analyze ./src
```

## SEE ALSO

- [Comprehensive CLI Documentation](CLI.md)
- [Setup Guide](SETUP.md)
- [Architecture Documentation](ARCHITECTURE.md)