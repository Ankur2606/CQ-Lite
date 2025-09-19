#!/usr/bin/env python3
"""
Test script for the new agentic LangGraph integration
"""

import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).parent))

from backend.agents.workflow import create_agentic_analysis_workflow
from backend.agents.state_schema import CodeAnalysisState

async def test_agentic_workflow():
    """Test the agentic workflow with the backend directory"""
    
    print("🤖 Testing LangGraph Agentic Workflow")
    print("=" * 50)
    

    workflow = create_agentic_analysis_workflow()
    

    initial_state = CodeAnalysisState(
        target_path="./backend",
        include_patterns=["*.py"],
        severity_filter=None,
        insights_requested=True,
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
        current_step="start",
        errors=[],
        analysis_complete=False,
        final_report=None
    )
    
    try:
        print("🔄 Executing agentic workflow...")
        result = await workflow.ainvoke(initial_state)
        
        print("\n✅ Workflow Results:")
        print(f"📁 Files discovered: {result.get('discovered_files', {})}")
        print(f"🧠 AI Strategy: {result.get('analysis_strategy', {})}")
        print(f"🔍 Issues found: {len(result.get('all_issues', []))}")
        print(f"📊 Current step: {result.get('current_step', 'unknown')}")
        
    
        issues = result.get('all_issues', [])
        if issues:
            print(f"\n🚨 Sample Issues (showing first 3 of {len(issues)}):")
            for i, issue in enumerate(issues[:3], 1):
                print(f"  {i}. {issue.severity.upper()} - {issue.title}")
                print(f"     📁 {issue.file_path}:{issue.line_number or 'N/A'}")
                print(f"     💡 {issue.suggestion[:100]}...")
                print()
        
        print("🎉 Agentic workflow test completed successfully!")
        
    except Exception as e:
        print(f"❌ Workflow failed: {e}")
        import traceback
        print(f"Debug: {traceback.format_exc()}")

if __name__ == "__main__":
    asyncio.run(test_agentic_workflow())