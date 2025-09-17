import click
import asyncio
import os
import sys
from pathlib import Path

# Add the parent directory to the path so we can import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.analyzers.code_analyzer import CodeAnalyzer
from backend.services.gemini_service import GeminiService
from cli.formatters import format_analysis_result, format_chat_response

@click.group()
def cli():
    """CQ Lite - AI-powered code analysis tool"""
    pass

@cli.command()
@click.argument('path', type=click.Path(exists=True))
@click.option('--format', '-f', type=click.Choice(['text', 'json']), default='text', help='Output format')
@click.option('--severity', '-s', type=click.Choice(['low', 'medium', 'high', 'critical']), help='Filter by severity')
@click.option('--insights', '-i', is_flag=True, help='Include detailed resolution steps for each issue')
def analyze(path, format, severity, insights):
    """Analyze code at the specified path"""
    click.echo(f"🔍 Analyzing code at: {path}")
    
    async def run_analysis():
        analyzer = CodeAnalyzer()
        result = await analyzer.analyze_path(path, generate_insights=insights)
        
        if severity:
            # Filter issues by severity
            result.issues = [issue for issue in result.issues if issue.severity == severity]
        
        if format == 'json':
            import json
            click.echo(json.dumps(result.dict(), indent=2, default=str))
        else:
            click.echo(format_analysis_result(result, show_insights=insights))
    
    asyncio.run(run_analysis())

@cli.command()
@click.option('--context', '-c', type=click.Path(exists=True), help='Path to analyzed code for context')
def chat(context):
    """Start interactive chat about your codebase"""
    click.echo("💬 Starting interactive chat session...")
    click.echo("Type 'exit' or 'quit' to end the session")
    
    async def run_chat():
        gemini_service = GeminiService()
        
        # Load context if provided
        context_data = None
        if context:
            click.echo(f"📁 Loading context from: {context}")
            analyzer = CodeAnalyzer()
            analysis_result = await analyzer.analyze_path(context)
            context_data = {"analysis_result": analysis_result.dict()}
        
        while True:
            try:
                user_input = click.prompt("\n🤔 Your question", type=str)
                
                if user_input.lower() in ['exit', 'quit', 'q']:
                    click.echo("👋 Goodbye!")
                    break
                
                response = await gemini_service.chat(user_input, context_data)
                click.echo(format_chat_response(response))
                
            except KeyboardInterrupt:
                click.echo("\n👋 Goodbye!")
                break
            except Exception as e:
                click.echo(f"❌ Error: {e}")
    
    asyncio.run(run_chat())

if __name__ == '__main__':
    cli()