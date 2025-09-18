import os
import json
from pathlib import Path
from typing import Dict, List
from backend.services.llm_service import get_llm_model
from .state_schema import CodeAnalysisState

def process_github_files(github_files: List[Dict]) -> Dict[str, List[str]]:
    """Process GitHub repository files and categorize by language"""
    discovered_files = {"python": [], "javascript": [], "docker": []}
    
    print(f"🔍 Processing {len(github_files)} GitHub files...")
    
    for file in github_files:
        file_path = file.get("file_path", "")
        filename = file_path.lower()
        # Use Path to extract extension, but keep original path as string
        ext = Path(file_path).suffix.lower()
        
        print(f"📄 Processing file: {file_path} (ext: {ext})")
        
        if ext == '.py':
            discovered_files["python"].append(file_path)
            print(f"✅ Added Python file: {file_path}")
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            discovered_files["javascript"].append(file_path)
            print(f"✅ Added JavaScript file: {file_path}")
        elif ext == '.dockerfile' or filename.endswith('dockerfile') or '/dockerfile' in filename or '\\dockerfile' in filename:
            discovered_files["docker"].append(file_path)
            print(f"✅ Added Docker file: {file_path}")
        else:
            print(f"⏭️ Skipping file: {file_path}")
    
    print(f"📊 Discovery results:")
    print(f"   Python files: {len(discovered_files['python'])}")
    print(f"   JavaScript files: {len(discovered_files['javascript'])}")
    print(f"   Docker files: {len(discovered_files['docker'])}")
    
    return discovered_files

def discover_files_by_language(target_path: str, include_patterns: List[str]) -> Dict[str, List[str]]:
    """Discover files and categorize by language"""
    discovered_files = {"python": [], "javascript": [], "docker": []}
    path_obj = Path(target_path)
    
    if path_obj.is_file():
        file_str = str(path_obj)
        filename = file_str.lower()
        ext = path_obj.suffix.lower()
        
        if ext == '.py':
            discovered_files["python"].append(file_str)
        elif ext in ['.js', '.ts', '.jsx', '.tsx']:
            discovered_files["javascript"].append(file_str)
        elif ext == '.dockerfile' or filename.endswith('dockerfile') or '/dockerfile' in filename or '\\dockerfile' in filename:
            discovered_files["docker"].append(file_str)
        return discovered_files
    
    # Special handling for Dockerfile (no extension)
    dockerfile = path_obj / "Dockerfile"
    if dockerfile.exists():
        discovered_files["docker"].append(str(dockerfile))
    
    for pattern in include_patterns:
        files = list(path_obj.rglob(pattern))
        for file_path in files:
            if file_path.is_file():
                file_str = str(file_path)
                filename = file_str.lower()
                ext = file_path.suffix.lower()
                
                if ext == '.py':
                    discovered_files["python"].append(file_str)
                elif ext in ['.js', '.ts', '.jsx', '.tsx']:
                    discovered_files["javascript"].append(file_str)
                elif ext == '.dockerfile' or filename.endswith('dockerfile') or '/dockerfile' in filename or '\\dockerfile' in filename:
                    discovered_files["docker"].append(file_str)
    
    return discovered_files

def parse_strategy_response(response_content: str) -> Dict[str, any]:
    """Parse AI strategy response with robust error handling"""
    print(f"🔍 Parsing strategy response: {response_content[:100]}...")
    
    try:
        # Clean the response text
        cleaned_text = response_content.strip()
        
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
            parsed = json.loads(json_text)
            print("✅ Successfully parsed strategy response JSON")
            return parsed
        else:
            print("❌ Could not find valid JSON in strategy response")
            raise ValueError("No valid JSON found in strategy response")
            
    except json.JSONDecodeError as e:
        print(f"❌ JSON decode error in strategy response: {e}")
    except Exception as e:
        print(f"❌ Error parsing strategy response: {e}")
    
    # Fallback strategy
    print("⚠️ Using fallback strategy due to parsing failure")
    return {
        "parallel_processing": True,
        "python_priority": True,
        "complexity_level": "moderate",
        "special_considerations": [],
        "error": "Failed to parse AI strategy response"
    }

def file_discovery_agent(state: CodeAnalysisState) -> CodeAnalysisState:
    """AI-powered file discovery and analysis strategy determination"""
    
    # If analysis was triggered from chat, use detected parameters
    target_path = state.get("detected_analysis_path") or state["target_path"]
    model_choice = state.get("detected_model_choice") or state.get("model_choice", "gemini")
    
    # Check if we're analyzing a GitHub repository
    is_github_repo = state.get("is_github_repo", False)
    github_files = state.get("github_files", [])
    
    if is_github_repo:
        print(f"🔍 Processing GitHub repository with {len(github_files)} files (model: {model_choice})")
        discovered_files = process_github_files(github_files)
    else:
        print(f"🔍 Discovering files in: {target_path} (model: {model_choice})")
        # Discover files using existing logic for local files
        discovered_files = discover_files_by_language(
            target_path, 
            state["include_patterns"]
        )
    
    # Get the selected model from the state
    llm_model = get_llm_model(model_choice)

    # AI Strategy Planning
    strategy_prompt = f"""Analyze this codebase structure and determine optimal analysis strategy:

Python files: {len(discovered_files.get('python', []))}
JavaScript files: {len(discovered_files.get('javascript', []))}
Total files: {sum(len(files) for files in discovered_files.values())}

Determine:
1. Analysis priority order (which language to analyze first)
2. Parallel vs sequential processing recommendation  
3. Expected complexity level (simple/moderate/complex)
4. Special considerations for this codebase type

IMPORTANT: You must respond with ONLY valid JSON. No additional text before or after.

Example response format:
{{
  "parallel_processing": true,
  "python_priority": true,
  "complexity_level": "moderate",
  "special_considerations": ["Large codebase", "Multiple frameworks"]
}}

Your response:"""
    
    analysis_strategy = {}
    try:
        if llm_model:
            print(f"🧠 Determining analysis strategy with {model_choice}...")
            strategy_response = llm_model.generate_content(strategy_prompt)
            analysis_strategy = parse_strategy_response(strategy_response.text)
        else:
            # If no model is available (e.g., no API keys), use a default strategy
            print("⚠️ No AI model available for strategy planning. Using default strategy.")
            raise Exception(f"{model_choice.capitalize()} API key not configured or model unavailable.")

    except Exception as e:
        # Fallback strategy if AI fails
        print(f"❌ AI strategy planning failed: {e}")
        analysis_strategy = {
            "parallel_processing": len(discovered_files.get('python', [])) > 0 and len(discovered_files.get('javascript', [])) > 0,
            "python_priority": len(discovered_files.get('python', [])) >= len(discovered_files.get('javascript', [])),
            "complexity_level": "moderate",
            "special_considerations": ["AI strategy planning failed, using default."],
            "error": str(e)
        }
    
    return {
        **state,
        "discovered_files": discovered_files,
        "analysis_strategy": analysis_strategy,
        "current_step": "discovery_complete"
    }