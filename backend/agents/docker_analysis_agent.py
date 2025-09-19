"""
Docker analysis agent for handling Docker file analysis in the workflow.
"""

import json
from typing import List, Dict, TypedDict
from backend.services.llm_service import get_llm_model
from backend.models.analysis_models import CodeIssue
from .state_schema import CodeAnalysisState
from backend.analyzers.docker_analyzer import DockerAnalyzer

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

    if github_files:
        from backend.analyzers.github_helpers import find_github_file_by_path
        github_file = find_github_file_by_path(github_files, file_path)
        if github_file:
            content = github_file.get("content", "")
            return content[:max_chars] + "..." if len(content) > max_chars else content
    

    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
            return content[:max_chars] + "..." if len(content) > max_chars else content
    except Exception:
        return "Could not read file content"

async def run_docker_analysis(file_path: str, github_files: List[Dict] = None) -> tuple[List[CodeIssue], any]:
    """
    Run Docker file analysis on a file, either from local path or GitHub repository.
    
    Args:
        file_path: Path to the file
        github_files: Optional list of GitHub file dictionaries
        
    Returns:
        Tuple of (issues, metrics)
    """
    analyzer = DockerAnalyzer()
    try:
        issues, metrics = await analyzer.analyze(file_path, github_files)
        return issues, metrics
    except Exception as e:
        print(f"❌ Error analyzing Docker file {file_path}: {e}")
        return [], None

def docker_analysis_agent(state: CodeAnalysisState) -> CodeAnalysisState:
    """AI-guided Docker file analysis with dynamic tool selection"""
    


    docker_files = []
    

    all_files = []
    for file_list in state["discovered_files"].values():
        all_files.extend(file_list)
    

    for file_path in all_files:
        filename = file_path.lower()
        if filename.endswith('dockerfile') or '/dockerfile' in filename or '\\dockerfile' in filename or '.dockerfile' in filename:
            docker_files.append(file_path)
    
    if not docker_files:
        print("📦 No Docker files found for analysis")
        return {
            **state, 
            "file_analysis_complete": {
                **state.get("file_analysis_complete", {}), 
                "docker": True
            }
        }
    

    model_choice = state.get("model_choice", "gemini")
    llm_model = get_llm_model(model_choice)

    docker_issues = []
    file_metadata = state.get("file_metadata", {})
    

    github_files = state.get("github_files", [])

    print(f"📦 Analyzing {len(docker_files)} Docker files...")
    
    for file_path in docker_files:
        print(f"📁 Analyzing: {file_path}")
    
        import asyncio
        issues, metrics = asyncio.run(run_docker_analysis(file_path, github_files))
        print(f"   Found {len(issues)} issues in {file_path}")
        
    
        file_content = read_file_content(file_path, github_files)
        analysis_prompt = f"""As a Docker and container security expert, analyze this Dockerfile and provide insights:

File: {file_path}
Issues Found: {len(issues)}
Code:
```dockerfile
{file_content}
```

Provide the following analysis:
1. Give a concise description of what this Dockerfile is building
2. Identify security vulnerabilities and their severity
3. Identify optimization opportunities to reduce image size and build time
4. Assess the use of best practices (multi-stage builds, layer reduction, etc.)
5. Provide specific improvement recommendations

IMPORTANT: You must respond with ONLY valid JSON. No additional text before or after.

Example response format:
{{
  "description": "Multi-stage Dockerfile that builds a Python web application with Alpine Linux.",
  "security_issues": [
    "HIGH: Container runs as root user, which is a security risk",
    "MEDIUM: Using pip without version pinning can lead to unexpected behaviors"
  ],
  "optimization_issues": [
    "Not using multi-stage builds increases image size",
    "Not combining RUN commands creates unnecessary layers"
  ],
  "best_practice_assessment": "Follows 4/10 best practices. Missing: multi-stage builds, layer reduction, .dockerignore, non-root user.",
  "recommendations": [
    "Add USER directive with non-root user",
    "Use multi-stage builds to separate build and runtime dependencies",
    "Combine RUN commands with && to reduce layers"
  ]
}}

Your response:"""
        try:
            if llm_model:
                print(f"   🧠 Enhancing analysis with {model_choice}...")
                ai_decisions = llm_model.generate_content(analysis_prompt)
                docker_issues.extend(issues)
                
            
                try:
                    ai_content = ai_decisions.text.strip()
                
                    if ai_content.startswith('```json'):
                        ai_content = ai_content[7:]
                    if ai_content.startswith('```'):
                        ai_content = ai_content[3:]
                    if ai_content.endswith('```'):
                        ai_content = ai_content[:-3]
                    
                    ai_content = ai_content.strip()
                
                    start_idx = ai_content.find('{')
                    end_idx = ai_content.rfind('}')
                    
                    if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                        ai_metadata = json.loads(ai_content[start_idx:end_idx + 1])
                        file_metadata[file_path] = {
                            "description": ai_metadata.get("description", ""),
                            "security_issues": ai_metadata.get("security_issues", []),
                            "optimization_issues": ai_metadata.get("optimization_issues", []),
                            "best_practice_assessment": ai_metadata.get("best_practice_assessment", ""),
                            "recommendations": ai_metadata.get("recommendations", [])
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
            
                print(f"   ⚠️ No AI model available for enhancement. Using static analysis results.")
                docker_issues.extend(issues)
                file_metadata[file_path] = {
                    "description": "AI enhancement skipped.",
                    "error": "No AI model available"
                }
        except Exception as e:
        
            print(f"   ❌ AI enhancement failed for {file_path}: {e}")
            docker_issues.extend(issues)
            file_metadata[file_path] = {
                "description": f"AI enhancement failed: {e}",
                "error": str(e)
            }
    
    print(f"📦 Docker analysis complete: {len(docker_issues)} total issues found")
    
    return {
        **state,
        "docker_issues": docker_issues,
        "all_issues": state.get("all_issues", []) + docker_issues,
        "file_metadata": file_metadata,
        "file_analysis_complete": {
            **state.get("file_analysis_complete", {}), 
            "docker": True
        },
        "current_step": "docker_analysis_complete"
    }