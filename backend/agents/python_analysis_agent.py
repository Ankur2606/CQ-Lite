import json
import re
import os
from typing import List, Dict
from backend.services.llm_service import get_llm_model
from backend.models.analysis_models import CodeIssue
from .state_schema import CodeAnalysisState
from backend.analyzers.python_analyzer import PythonAnalyzer

def read_file_content(file_path: str, max_chars: int = 2000) -> str:
    """Read file content with size limit"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return content[:max_chars] + "..." if len(content) > max_chars else content
    except Exception:
        return "Could not read file content"

def merge_and_enhance_issues(ast_issues: List[CodeIssue], ai_decisions: str, file_path: str) -> tuple[List[CodeIssue], Dict[str, any]]:
    """Merge traditional analysis with AI enhancements and return file metadata"""
    print(f"🔍 Parsing AI decisions for {file_path}: {ai_decisions[:100]}...")
    
    # Default metadata
    file_metadata = {
        "truncated": False,
        "description": "",
        "enhanced_suggestions": {},
        "business_impact": "",
        "architectural_concerns": []
    }
    
    try:
        # Clean the response text
        cleaned_text = ai_decisions.strip()
        
        # Remove any markdown code blocks if present
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        
        cleaned_text = cleaned_text.strip()
        
        # Try to find JSON object boundaries
        start_idx = cleaned_text.find('{')
        end_idx = cleaned_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_text = cleaned_text[start_idx:end_idx + 1]
            ai_data = json.loads(json_text)
            print("✅ Successfully parsed AI decisions JSON")
            
            # Extract file metadata
            file_metadata = {
                "truncated": ai_data.get('truncated', False),
                "description": ai_data.get('description', ''),
                "enhanced_suggestions": ai_data.get('enhanced_suggestions', {}),
                "business_impact": ai_data.get('business_impact', ''),
                "architectural_concerns": ai_data.get('architectural_concerns', [])
            }
            
            # Enhance existing issues with AI insights
            enhanced_issues = []
            for issue in ast_issues:
                # Add AI enhancement to suggestion if available
                ai_enhancement = ai_data.get('enhanced_suggestions', {}).get(issue.id, '')
                if ai_enhancement:
                    issue.suggestion = f"{issue.suggestion}\n\n🤖 AI Enhancement: {ai_enhancement}"
                enhanced_issues.append(issue)
            
            return enhanced_issues, file_metadata
        else:
            print("❌ Could not find valid JSON in AI decisions")
            raise ValueError("No valid JSON found in AI decisions")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in AI decisions: {e}")
    except Exception as e:
        print(f"❌ Error parsing AI decisions: {e}")
    
    # Return original issues if AI enhancement fails
    print("⚠️ Using original issues due to AI parsing failure")
    return ast_issues, file_metadata

async def run_python_analysis(file_path: str) -> tuple[List[CodeIssue], any]:
    """Run traditional Python analysis"""
    analyzer = PythonAnalyzer()
    try:
        issues, metrics = await analyzer.analyze(file_path)
        return issues, metrics
    except Exception as e:
        return [], None

def python_analysis_agent(state: CodeAnalysisState) -> CodeAnalysisState:
    """AI-guided Python analysis with dynamic tool selection"""
    
    python_files = state["discovered_files"].get("python", [])
    if not python_files:
        return {
            **state, 
            "file_analysis_complete": {
                **state.get("file_analysis_complete", {}), 
                "python": True
            }
        }
    
    # Get the selected model from the state
    model_choice = state.get("model_choice", "gemini")
    llm_model = get_llm_model(model_choice)

    python_issues = []
    file_metadata = state.get("file_metadata", {})

    print(f"🐍 Analyzing {len(python_files)} Python files...")
    
    for file_path in python_files[:5]:  # Limit for demo
        print(f"📁 Analyzing: {file_path}")
        # Traditional AST + Tool Analysis
        import asyncio
        ast_issues, metrics = asyncio.run(run_python_analysis(file_path))
        print(f"   Found {len(ast_issues)} issues in {file_path}")
        
        # AI-Enhanced Analysis Decision Making
        file_content = read_file_content(file_path)
        analysis_prompt = f"""As a Python code quality expert, analyze this file and make decisions:

File: {file_path}
Issues Found: {len(ast_issues)}
Code Sample: {file_content}

Decisions needed:
1. Should we run additional deep analysis on this file?
2. Are the detected issues accurate or false positives?
3. What's the business impact severity of issues found?
4. Are there patterns suggesting architectural problems?
5. **TRUNCATION DECISION**: Is this file simple enough that a brief description would suffice for AI review? Consider truncating if:
   - File has 0-1 minor issues (like missing docstrings)
   - File is mostly boilerplate (like __init__.py)
   - File is very short and straightforward
   - No complex business logic or security concerns
6. Generate a concise description of the file's purpose, main functions, and classes.

IMPORTANT: You must respond with ONLY valid JSON. No additional text before or after.

Example response format:
{{
  "deep_analysis_needed": true,
  "enhanced_suggestions": {{
    "issue_id_1": "This function violates SRP. Consider splitting into data fetching and validation functions.",
    "issue_id_2": "This nested loop can be optimized using dictionary lookup for O(n) complexity."
  }},
  "false_positives": ["issue_id_3"],
  "business_impact": "High - affects user experience and security",
  "architectural_concerns": ["Tight coupling detected", "Missing error handling patterns"],
  "truncated": false,
  "description": "Main application entry point with FastAPI setup, file upload endpoints, and CORS configuration. Contains uvicorn server startup logic."
}}

Example for simple file (should be truncated):
{{
  "deep_analysis_needed": false,
  "enhanced_suggestions": {{}},
  "false_positives": [],
  "business_impact": "Low - simple utility file",
  "architectural_concerns": [],
  "truncated": true,
  "description": "Simple utility function that returns a greeting string. No complex logic or security concerns."
}}

Your response:"""
        try:
            if llm_model:
                print(f"   🧠 Enhancing analysis with {model_choice}...")
                ai_decisions = llm_model.generate_content(analysis_prompt)
                enhanced_issues, metadata = merge_and_enhance_issues(
                    ast_issues, 
                    ai_decisions.text, 
                    file_path
                )
                print(f"   📊 File {file_path} - Truncated: {metadata.get('truncated', False)}")
                python_issues.extend(enhanced_issues)
                file_metadata[file_path] = metadata
            else:
                # Fallback to original issues if AI not available
                print(f"   ⚠️ No AI model available for enhancement. Using static analysis results.")
                python_issues.extend(ast_issues)
                file_metadata[file_path] = {
                    "truncated": False,
                    "description": "AI enhancement skipped.",
                    "enhanced_suggestions": {},
                    "business_impact": "",
                    "architectural_concerns": []
                }
        except Exception as e:
            # Fallback to original issues if AI fails
            print(f"   ❌ AI enhancement failed for {file_path}: {e}")
            python_issues.extend(ast_issues)
            file_metadata[file_path] = {
                "truncated": False,
                "description": f"AI enhancement failed: {e}",
                "enhanced_suggestions": {},
                "business_impact": "",
                "architectural_concerns": []
            }
    
    print(f"🐍 Python analysis complete: {len(python_issues)} total issues found")
    
    return {
        **state,
        "python_issues": python_issues,
        "all_issues": state.get("all_issues", []) + python_issues,
        "file_metadata": file_metadata,
        "file_analysis_complete": {
            **state.get("file_analysis_complete", {}), 
            "python": True
        },
        "current_step": "python_analysis_complete"
    }