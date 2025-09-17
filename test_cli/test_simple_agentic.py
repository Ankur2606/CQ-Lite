#!/usr/bin/env python3
"""
Simple test for agentic functionality without complex dependencies
"""

import asyncio
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Add backend to path
sys.path.append(str(Path(__file__).parent))

# Load environment
load_dotenv()

def test_environment():
    """Test if environment is properly configured"""
    print("🔧 Testing Environment Configuration")
    print("=" * 40)
    
    # Check API key
    api_key = os.getenv('GOOGLE_API_KEY')
    if api_key:
        print(f"✅ GOOGLE_API_KEY found: {api_key[:10]}...")
    else:
        print("❌ GOOGLE_API_KEY not found in environment")
        return False
    
    # Test Google Generative AI import
    try:
        import google.generativeai as genai
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-2.5-flash')
        print("✅ Google Generative AI configured successfully")
        
        # Test simple generation
        response = model.generate_content("Say hello")
        print(f"✅ Test generation successful: {response.text[:50]}...")
        
    except Exception as e:
        print(f"❌ Google Generative AI test failed: {e}")
        return False
    
    return True

def test_file_discovery():
    """Test file discovery functionality"""
    print("\n📁 Testing File Discovery")
    print("=" * 40)
    
    try:
        from backend.agents.file_discovery_agent import discover_files_by_language
        
        files = discover_files_by_language("./backend", ["*.py"])
        print(f"✅ Discovered {len(files.get('python', []))} Python files")
        print(f"   Sample files: {files.get('python', [])[:3]}")
        
        return True
    except Exception as e:
        print(f"❌ File discovery failed: {e}")
        return False

async def test_basic_workflow():
    """Test basic workflow without full LangGraph"""
    print("\n🤖 Testing Basic Agent Workflow")
    print("=" * 40)
    
    try:
        from backend.agents.file_discovery_agent import file_discovery_agent
        from backend.agents.state_schema import CodeAnalysisState
        
        # Create minimal state
        state = CodeAnalysisState(
            target_path="./backend",
            include_patterns=["*.py"],
            severity_filter=None,
            insights_requested=False,
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
        
        # Test file discovery agent
        result = file_discovery_agent(state)
        
        print(f"✅ File discovery completed")
        print(f"   Files found: {result.get('discovered_files', {})}")
        print(f"   AI Strategy: {result.get('analysis_strategy', {})}")
        print(f"   Current step: {result.get('current_step', 'unknown')}")
        
        return True
        
    except Exception as e:
        print(f"❌ Basic workflow test failed: {e}")
        import traceback
        print(f"   Debug: {traceback.format_exc()}")
        return False

async def main():
    """Run all tests"""
    print("🧪 Agentic System Test Suite")
    print("=" * 50)
    
    tests_passed = 0
    total_tests = 3
    
    # Test 1: Environment
    if test_environment():
        tests_passed += 1
    
    # Test 2: File Discovery
    if test_file_discovery():
        tests_passed += 1
    
    # Test 3: Basic Workflow
    if await test_basic_workflow():
        tests_passed += 1
    
    print(f"\n📊 Test Results: {tests_passed}/{total_tests} tests passed")
    
    if tests_passed == total_tests:
        print("🎉 All tests passed! Agentic system is ready.")
    else:
        print("⚠️  Some tests failed. Check the errors above.")

if __name__ == "__main__":
    asyncio.run(main())