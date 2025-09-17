import json
from typing import List, Dict, TypedDict
from backend.services.llm_service import get_llm_model
from backend.models.analysis_models import CodeIssue
from .state_schema import CodeAnalysisState
from backend.analyzers.javascript_analyzer import JavaScriptAnalyzer

def read_file_content(file_path: str, github_files: List[Dict] = None, max_chars: int = 2000) -> str:
    """
    Read file content with size limit, either from local file or GitHub data.
    
    Args:
        file_path: Path to the file
        github_files: Optional list of GitHub file dictionaries
        max_chars: Maximum number of characters to read
        
    Returns:
        File content or error message
    """
    # Check if we have GitHub files
    if github_files:
        from backend.analyzers.github_helpers import find_github_file_by_path
        github_file = find_github_file_by_path(github_files, file_path)
        if github_file:
            content = github_file.get("content", "")
            return content[:max_chars] + "..." if len(content) > max_chars else content
    
    # Fall back to local file
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return content[:max_chars] + "..." if len(content) > max_chars else content
    except Exception:
        return "Could not read file content"

async def run_javascript_analysis(file_path: str, github_files: List[Dict] = None) -> tuple[List[CodeIssue], any]:
    """
    Run traditional JavaScript analysis on a file, either from local path or GitHub repository.
    
    Args:
        file_path: Path to the file
        github_files: Optional list of GitHub file dictionaries
        
    Returns:
        Tuple of (issues, metrics)
    """
    analyzer = JavaScriptAnalyzer()
    try:
        issues, metrics = await analyzer.analyze(file_path, github_files)
        return issues, metrics
    except Exception as e:
        print(f"❌ Error analyzing JavaScript file {file_path}: {e}")
        return [], None

def javascript_analysis_agent(state: CodeAnalysisState) -> CodeAnalysisState:
    """AI-guided JavaScript analysis with dynamic tool selection"""
    
    js_files = state["discovered_files"].get("javascript", [])
    if not js_files:
        return {
            **state, 
            "file_analysis_complete": {
                **state.get("file_analysis_complete", {}), 
                "javascript": True
            }
        }
    
    # Get the selected model from the state
    model_choice = state.get("model_choice", "gemini")
    llm_model = get_llm_model(model_choice)

    js_issues = []
    file_metadata = state.get("file_metadata", {})
    
    # Check for GitHub files in state
    github_files = state.get("github_files", [])

    print(f"🟨 Analyzing {len(js_files)} JavaScript files...")
    
    for file_path in js_files[:10]:  # Limit for demo
        print(f"📁 Analyzing: {file_path}")
        # Traditional AST + Tool Analysis
        import asyncio
        ast_issues, metrics = asyncio.run(run_javascript_analysis(file_path, github_files))
        print(f"   Found {len(ast_issues)} issues in {file_path}")
        
        # AI-Enhanced Analysis Decision Making
        file_content = read_file_content(file_path, github_files)
        analysis_prompt = f"""As a JavaScript code quality expert, analyze this file and provide insights:

File: {file_path}
Issues Found: {len(ast_issues)}
Code Sample: {file_content}

Decisions needed:
1. Provide a concise description of the file's purpose, main functions, and components.
2. What are the key areas of concern in this JavaScript file?
3. Are there security risks like XSS, injection vulnerabilities, or unsafe DOM operations?
4. Are there performance issues like inefficient loops or memory leaks?
5. Are there React-specific issues (if applicable) like proper hooks usage?

IMPORTANT: You must respond with ONLY valid JSON. No additional text before or after.

Example response format:
{{
  "description": "React component that handles user authentication UI with form validation.",
  "key_concerns": ["Form validation could be improved", "Missing error handling for API responses"],
  "security_issues": ["Potential XSS in user input rendering", "Credentials stored in state"],
  "performance_issues": ["Inefficient re-renders due to missing memoization"],
  "react_specific_issues": ["useEffect missing dependencies", "State updates in render phase"]
}}

Your response:"""
        try:
            if llm_model:
                print(f"   🧠 Enhancing analysis with {model_choice}...")
                ai_decisions = llm_model.generate_content(analysis_prompt)
                js_issues.extend(ast_issues)
                
                # Parse AI analysis and add to file metadata
                try:
                    ai_content = ai_decisions.text.strip()
                    # Handle markdown formatting if present
                    if ai_content.startswith('```json'):
                        ai_content = ai_content[7:]
                    if ai_content.startswith('```'):
                        ai_content = ai_content[3:]
                    if ai_content.endswith('```'):
                        ai_content = ai_content[:-3]
                    
                    ai_content = ai_content.strip()
                    # Find JSON boundaries
                    start_idx = ai_content.find('{')
                    end_idx = ai_content.rfind('}')
                    
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        ai_metadata = json.loads(ai_content[start_idx:end_idx + 1])
                        file_metadata[file_path] = {
                            "description": ai_metadata.get("description", ""),
                            "key_concerns": ai_metadata.get("key_concerns", []),
                            "security_issues": ai_metadata.get("security_issues", []),
                            "performance_issues": ai_metadata.get("performance_issues", []),
                            "react_specific_issues": ai_metadata.get("react_specific_issues", [])
                        }
                    else:
                        file_metadata[file_path] = {
                            "description": "Failed to parse AI analysis.",
                            "error": "Could not find valid JSON in AI response"
                        }
                except Exception as e:
                    print(f"   ❌ Error parsing AI analysis for {file_path}: {e}")
                    file_metadata[file_path] = {
                        "description": f"Error parsing AI analysis: {str(e)}",
                        "error": str(e)
                    }
            else:
                # Fallback to original issues if AI not available
                print(f"   ⚠️ No AI model available for enhancement. Using static analysis results.")
                js_issues.extend(ast_issues)
                file_metadata[file_path] = {
                    "description": "AI enhancement skipped.",
                    "error": "No AI model available"
                }
        except Exception as e:
            # Fallback to original issues if AI fails
            print(f"   ❌ AI enhancement failed for {file_path}: {e}")
            js_issues.extend(ast_issues)
            file_metadata[file_path] = {
                "description": f"AI enhancement failed: {e}",
                "error": str(e)
            }
    
    print(f"🟨 JavaScript analysis complete: {len(js_issues)} total issues found")
    
    return {
        **state,
        "javascript_issues": js_issues,
        "all_issues": state.get("all_issues", []) + js_issues,
        "file_metadata": file_metadata,
        "file_analysis_complete": {
            **state.get("file_analysis_complete", {}), 
            "javascript": True
        },
        "current_step": "javascript_analysis_complete"
    }