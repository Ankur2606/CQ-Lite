import click
import asyncio
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
load_dotenv()
# Add the parent directory to the path so we can import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.agents.workflow import create_agentic_analysis_workflow
from backend.agents.state_schema import CodeAnalysisState
from cli.formatters import format_analysis_result
from cli.env_helpers import (
    check_github_token, 
    check_notion_credentials, 
    check_ai_credentials,
    print_env_var_help,
    MissingEnvVarError
)

# Initialize the agentic workflow
agentic_workflow = create_agentic_analysis_workflow()

@click.group()
def cli():
    """Code Quality Intelligence Agent - Agentic AI-powered analysis"""
    pass

@cli.command()
def env():
    """Show information about required environment variables"""
    click.echo("📝 Code Quality Reviewer - Environment Variables Guide")
    click.echo("\nThis tool requires various API keys for full functionality.")
    
    # Check status of all environment variables
    github_token = os.environ.get("GITHUB_API_TOKEN")
    google_api_key = os.environ.get("GOOGLE_API_KEY")
    nebius_api_key = os.environ.get("NEBIUS_API_KEY")
    notion_token = os.environ.get("NOTION_TOKEN")
    notion_page_id = os.environ.get("NOTION_PAGE_ID")
    
    click.echo("\nCurrent Environment Status:")
    click.echo(f"  ✓ GITHUB_API_TOKEN: {'Set' if github_token else 'Not set'} - Required for GitHub repository analysis")
    click.echo(f"  ✓ GOOGLE_API_KEY: {'Set' if google_api_key else 'Not set'} - Required for Gemini AI analysis")
    click.echo(f"  ✓ NEBIUS_API_KEY: {'Set' if nebius_api_key else 'Not set'} - Required for Nebius AI analysis")
    click.echo(f"  ✓ NOTION_TOKEN: {'Set' if notion_token else 'Not set'} - Required for Notion integration")
    click.echo(f"  ✓ NOTION_PAGE_ID: {'Set' if notion_page_id else 'Not set'} - Required for Notion integration")
    
    # Print detailed setup instructions for any missing variables
    missing = []
    if not github_token:
        missing.append("GITHUB_API_TOKEN")
    if not google_api_key:
        missing.append("GOOGLE_API_KEY")
    if not nebius_api_key:
        missing.append("NEBIUS_API_KEY")
    if not notion_token:
        missing.append("NOTION_TOKEN")
    if not notion_page_id:
        missing.append("NOTION_PAGE_ID")
    
    if missing:
        print_env_var_help(missing)
    else:
        click.echo("\n✅ All environment variables are set. You're good to go!")

@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
@click.option('--repourl', '-r', help='GitHub repository URL to analyze')
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.option('--severity', '-s', type=click.Choice(['low', 'medium', 'high', 'critical']), help='Filter by severity')
@click.option('--insights', '-i', is_flag=True, help='Generate AI insights')
@click.option('--model', type=click.Choice(['gemini', 'nebius']), default='gemini', help='Choose the AI model for analysis')
@click.option('--quick', is_flag=True, help='Run a quick analysis, skipping vector store and using Nebius model.')
@click.option('--notion', is_flag=True, help='Push analysis results to Notion (requires NOTION_TOKEN and NOTION_PAGE_ID env vars)')
@click.option('--max-files', type=int, default=100, help='Maximum number of files to analyze when using --repourl')
def analyze(path, repourl, format, severity, insights, model, quick, notion, max_files):
    """Agentic code analysis using LangGraph orchestration"""
    
    # Ensure either path or repourl is provided
    if not path and not repourl:
        click.echo("❌ Error: Either PATH or --repourl must be provided", err=True)
        return 1
    
    # Check AI API credentials are available
    if not check_ai_credentials(model):
        click.echo(f"❌ Error: Missing AI credentials for {model} model", err=True)
        return 1
    
    # Handle GitHub repository URL
    github_files = []
    target_path = path or "github-repo"
    
    if repourl:
        # Check GitHub API token is available
        if not check_github_token():
            click.echo("❌ Error: GitHub API token is required for repository analysis", err=True)
            return 1
            
        from backend.tools.github_tool import fetch_repo_files, GitHubAPIException, parse_github_url
        
        try:
            click.echo(f"🔍 Fetching code from GitHub repository: {repourl}")
            repo_info = parse_github_url(repourl)
            click.echo(f"📦 Repository: {repo_info['owner']}/{repo_info['repo']}")
            
            # Fetch repository files
            github_files = fetch_repo_files(repourl, max_files=max_files)
            click.echo(f"📚 Downloaded {len(github_files)} files for analysis")
            
            # Use repo name as target path if no path is provided
            if not path:
                target_path = f"github-repo-{repo_info['owner']}-{repo_info['repo']}"
                
        except (GitHubAPIException, ValueError) as e:
            click.echo(f"❌ GitHub error: {str(e)}", err=True)
            return 1
        except Exception as e:
            click.echo(f"❌ Unexpected error: {str(e)}", err=True)
            return 1
    
    if quick:
        model = 'nebius'
        click.echo(f"🚀 Running quick analysis of: {target_path} using {model} model, skipping vector store.")
    else:
        click.echo(f"🤖 Starting agentic analysis of: {target_path} using {model} model")
    
    if notion:
        click.echo("📝 Notion reporting enabled - results will be pushed to Notion")
        # Check if Notion credentials are set
        if not check_notion_credentials():
            click.echo("⚠️  Warning: Notion reporting will be skipped due to missing credentials.")
    
    async def run_agentic_analysis():
        # Initialize agent state from CLI parameters
        initial_state = CodeAnalysisState(
            target_path=target_path,
            include_patterns=["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"],
            severity_filter=severity,
            insights_requested=insights,
            model_choice=model,  # Pass model choice to the state
            skip_vector_store=quick,
            chat_mode=False,
            discovered_files={},
            file_analysis_complete={},
            all_issues=[],
            python_issues=[],
            javascript_issues=[],
            file_metrics=[],
            analysis_strategy={},
            current_batch=[],
            ai_insights_complete=False,
            conversation_history=[],
            current_query="",
            analysis_context={},
            analysis_requested=False,
            detected_analysis_path=None,
            detected_model_choice=None,
            notion_reporting_enabled=notion,
            current_step="start",
            errors=[],
            analysis_complete=False,
            final_report=None,
            github_files=github_files if github_files else [],
            is_github_repo=bool(repourl)
        )
        
        try:
            # Execute agentic workflow
            click.echo("🔄 Executing AI agent workflow...")
            result = await agentic_workflow.ainvoke(initial_state)
            
            # Display results
            click.echo(f"✅ Analysis complete! Current step: {result.get('current_step', 'unknown')}")
            click.echo(f"📊 Files discovered: {result.get('discovered_files', {})}")
            click.echo(f"🔍 Issues found: {len(result.get('all_issues', []))}")
            
            # Show AI review summary if available
            ai_review = result.get("ai_review", {})
            if ai_review:
                click.echo(f"\n🤖 AI COMPREHENSIVE REVIEW:")
                click.echo(f"📋 Executive Summary: {ai_review.get('executive_summary', 'N/A')}")
                
                quality_metrics = ai_review.get("quality_metrics", {})
                if quality_metrics:
                    click.echo(f"📊 Overall Quality Score: {quality_metrics.get('overall_score', 'N/A')}/10")
                    click.echo(f"🔒 Security Score: {quality_metrics.get('security_score', 'N/A')}/10")
                    click.echo(f"🔧 Maintainability Score: {quality_metrics.get('maintainability_score', 'N/A')}/10")
                
                recommendations = ai_review.get("recommendations", {})
                if recommendations.get("immediate_actions"):
                    click.echo(f"⚡ Immediate Actions: {recommendations['immediate_actions']}")
            
            # Format output if we have issues
            if result.get("all_issues"):
                # Create a mock AnalysisResult for formatting
                from backend.models.analysis_models import AnalysisResult, IssueSeverity
                
                # Sort issues by severity
                severity_order = {
                    IssueSeverity.CRITICAL: 4,
                    IssueSeverity.HIGH: 3,
                    IssueSeverity.MEDIUM: 2,
                    IssueSeverity.LOW: 1
                }
                sorted_issues = sorted(
                    result["all_issues"],
                    key=lambda issue: severity_order.get(issue.severity, 0),
                    reverse=True
                )
                
                # Calculate severity breakdown
                severity_breakdown = {}
                for issue in sorted_issues:
                    severity_breakdown[issue.severity] = severity_breakdown.get(issue.severity, 0) + 1
                
                mock_result = AnalysisResult(
                    summary={
                        "total_issues": len(sorted_issues),
                        "severity_breakdown": severity_breakdown,
                        "languages_detected": list(result.get("discovered_files", {}).keys()),
                        "ai_review_summary": ai_review.get("executive_summary", "")
                    },
                    issues=sorted_issues,
                    metrics=result.get("file_metrics", []),
                    total_files=sum(len(files) for files in result.get("discovered_files", {}).values()),
                    total_lines=0,
                    analysis_duration=0.0
                )
                
                if format == 'json':
                    import json
                    # Include AI review in JSON output
                    output_data = mock_result.dict()
                    output_data["ai_review"] = ai_review
                    click.echo(json.dumps(output_data, indent=2, default=str))
                else:
                    click.echo(format_analysis_result(mock_result, show_insights=True))
            
        except Exception as e:
            click.echo(f"❌ Analysis failed: {str(e)}", err=True)
            import traceback
            click.echo(f"Debug info: {traceback.format_exc()}", err=True)
            return 1
    
    asyncio.run(run_agentic_analysis())

@cli.command()
@click.argument('path', type=click.Path(exists=True), required=False)
@click.option('--repourl', '-r', help='GitHub repository URL to analyze')
@click.option('--format', '-f', type=click.Choice(['text', 'json', 'md', 'html', 'notion']), default='text', help='Output format')
@click.option('--service', type=click.Choice(['gemini', 'nebius']), default='gemini', help='AI service to use for report generation')
@click.option('--notion', is_flag=True, help='Push comprehensive report to Notion (requires NOTION_TOKEN and NOTION_PAGE_ID env vars)')
@click.option('--max-files', type=int, default=100, help='Maximum number of files to analyze when using --repourl')
def review(path, repourl, format, service, notion, max_files):
    """Generate a comprehensive code review with analysis and recommendations"""
    # Always enable insights for reviews
    insights = True
    
    # If notion is specified as format or flag, enable Notion reporting
    notion_enabled = notion or format == 'notion'
    
    if not path and not repourl:
        click.echo("❌ Error: Either PATH or --repourl must be provided", err=True)
        return 1
    
    # Check AI API credentials are available
    if not check_ai_credentials(service):
        click.echo(f"❌ Error: Missing AI credentials for {service} model", err=True)
        return 1
    
    # If GitHub repo URL is provided, check for GitHub token
    if repourl and not check_github_token():
        click.echo("❌ Error: GitHub API token is required for repository analysis", err=True)
        return 1
    
    # Check Notion credentials if Notion reporting is enabled
    if notion_enabled and not check_notion_credentials():
        click.echo("⚠️  Warning: Notion reporting will be skipped due to missing credentials.")
    
    # This is a wrapper around analyze with pre-configured options optimized for reviews
    click.echo(f"📝 Generating comprehensive code review using {service} AI service")
    
    if notion_enabled:
        click.echo("📊 Review will be pushed to Notion")
    
    # Call analyze with review-optimized parameters
    return analyze(
        path=path,
        repourl=repourl,
        format=format if format != 'notion' else 'text',  # Handle notion format specially
        severity=None,  # Include all severities
        insights=True,  # Always enable insights
        model=service,
        quick=False,  # Never use quick mode for reviews
        notion=notion_enabled,
        max_files=max_files
    )

@cli.command()
@click.option('--context', '-c', type=click.Path(exists=True), help='Path to analyzed code for context')
@click.option('--notion', is_flag=True, help='Push analysis results to Notion when analysis is triggered (requires NOTION_TOKEN and NOTION_PAGE_ID env vars)')
def chat(context, notion):
    """Interactive Q&A using agentic workflow with analysis triggering"""
    # Check AI API credentials are available (default to gemini model)
    if not check_ai_credentials("gemini"):
        click.echo("❌ Error: Missing AI credentials for chat functionality", err=True)
        return 1
    
    # Check Notion credentials if Notion reporting is enabled
    if notion and not check_notion_credentials():
        click.echo("⚠️  Warning: Notion reporting will be skipped due to missing credentials.")
    
    click.echo("💬 Agentic chat mode activated!")
    click.echo("You can ask questions about your code or request analysis (e.g., 'analyze ./cli' or 'review the codebase at ./src')")
    
    if context:
        click.echo(f"📁 Context loaded from: {context}")
    
    # Initialize chat state
    from langchain_core.messages import HumanMessage, AIMessage
    
    conversation_history = []
    
    while True:
        try:
            user_input = click.prompt("You")
            
            if user_input.lower() in ['exit', 'quit', 'bye']:
                click.echo("👋 Goodbye!")
                break
            
            # Add user message to history
            conversation_history.append(HumanMessage(content=user_input))
            
            # Initialize agent state for this query
            initial_state = CodeAnalysisState(
                target_path=context or ".",  # Use context path or current directory
                include_patterns=["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"],
                severity_filter=None,
                insights_requested=True,
                model_choice="gemini",
                skip_vector_store=False,
                chat_mode=True,
                discovered_files={},
                file_analysis_complete={},
                all_issues=[],
                python_issues=[],
                javascript_issues=[],
                file_metrics=[],
                analysis_strategy={},
                current_batch=[],
                ai_insights_complete=False,
                conversation_history=conversation_history,
                current_query=user_input,
                analysis_context={},
                analysis_requested=False,
                detected_analysis_path=None,
                detected_model_choice=None,
                notion_reporting_enabled=notion,
                current_step="chat_start",
                errors=[],
                analysis_complete=False,
                final_report=None
            )
            
            async def run_chat_query():
                try:
                    result = await agentic_workflow.ainvoke(initial_state)
                    
                    # Get the latest response from conversation history
                    if result.get("conversation_history"):
                        last_message = result["conversation_history"][-1]
                        if hasattr(last_message, 'content'):
                            response = last_message.content
                        else:
                            response = str(last_message)
                        
                        click.echo(f"\n🤖 Assistant: {response}")
                        
                        # Add assistant response to history
                        conversation_history.append(AIMessage(content=response))
                    
                    # If analysis was triggered, show analysis results
                    if result.get("analysis_requested"):
                        click.echo(f"\n📊 Analysis triggered for: {result.get('detected_analysis_path')}")
                        click.echo(f"📈 Analysis complete! Found {len(result.get('all_issues', []))} issues")
                        
                        # Show summary if available
                        if result.get("final_report"):
                            report = result["final_report"]
                            click.echo(f"📋 Total files: {report.total_files}")
                            click.echo(f"🔍 Total issues: {len(report.issues)}")
                    
                except Exception as e:
                    click.echo(f"❌ Error: {str(e)}")
            
            asyncio.run(run_chat_query())
            
        except KeyboardInterrupt:
            click.echo("\n👋 Goodbye!")
            break
        except click.Abort:
            click.echo("\n👋 Goodbye!")
            break

def check_env_setup():
    """Check if environment variables are set up and provide a gentle reminder if not."""
    # Check for key environment variables
    has_github = os.environ.get("GITHUB_API_TOKEN") is not None
    has_ai = (os.environ.get("GOOGLE_API_KEY") is not None or
              os.environ.get("NEBIUS_API_KEY") is not None)
    
    if not has_github or not has_ai:
        click.echo("⚠️  Some environment variables are missing. Some features may not work properly.")
        click.echo("💡 Run 'python -m cli env' for setup information.")

if __name__ == '__main__':
    check_env_setup()
    cli()