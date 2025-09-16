import click
import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.agents.workflow import create_agentic_analysis_workflow
from backend.agents.state_schema import CodeAnalysisState
from cli.formatters import format_analysis_result

# Initialize the agentic workflow
agentic_workflow = create_agentic_analysis_workflow()

@click.group()
def cli():
    """Code Quality Intelligence Agent - Agentic AI-powered analysis"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.option('--severity', '-s', type=click.Choice(['low', 'medium', 'high', 'critical']), help='Filter by severity')
@click.option('--insights', '-i', is_flag=True, help='Generate AI insights')
@click.option('--model', type=click.Choice(['gemini', 'nebius']), default='gemini', help='Choose the AI model for analysis')
@click.option('--quick', is_flag=True, help='Run a quick analysis, skipping vector store and using Nebius model.')
@click.option('--notion', is_flag=True, help='Push analysis results to Notion (requires NOTION_TOKEN and NOTION_PAGE_ID env vars)')
def analyze(path, format, severity, insights, model, quick, notion):
    """Agentic code analysis using LangGraph orchestration"""
    
    if quick:
        model = 'nebius'
        click.echo(f"🚀 Running quick analysis of: {path} using {model} model, skipping vector store.")
    else:
        click.echo(f"🤖 Starting agentic analysis of: {path} using {model} model")
    
    if notion:
        click.echo("📝 Notion reporting enabled - results will be pushed to Notion")
        # Check if environment variables are set
        import os
        if not os.getenv("NOTION_TOKEN") or not os.getenv("NOTION_PAGE_ID"):
            click.echo("⚠️  Warning: NOTION_TOKEN and/or NOTION_PAGE_ID not set. Notion reporting will be skipped.")
    
    async def run_agentic_analysis():
        # Initialize agent state from CLI parameters
        initial_state = CodeAnalysisState(
            target_path=path,
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
            final_report=None
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
@click.option('--context', '-c', type=click.Path(exists=True), help='Path to analyzed code for context')
@click.option('--notion', is_flag=True, help='Push analysis results to Notion when analysis is triggered (requires NOTION_TOKEN and NOTION_PAGE_ID env vars)')
def chat(context, notion):
    """Interactive Q&A using agentic workflow with analysis triggering"""
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

if __name__ == '__main__':
    cli()