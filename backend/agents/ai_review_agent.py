import os
import json
import re
from typing import List, Dict, Any
from backend.services.llm_service import get_llm_model
from backend.models.analysis_models import CodeIssue, IssueSeverity, IssueCategory
from .state_schema import CodeAnalysisState

def read_codebase_context(discovered_files: Dict[str, List[str]], file_metadata: Dict[str, Dict] = None, 
                       github_files: List[Dict] = None, force_full_content: bool = False) -> Dict[str, str]:
    """
    Read the entire codebase for AI context with intelligent truncation.
    Works with both local files and GitHub repository files.
    """
    codebase_context = {}
    
    for language, files in discovered_files.items():
        for file_path in files:
            try:
                # Check if we have GitHub files
                content = None
                if github_files:
                    from backend.analyzers.github_helpers import find_github_file_by_path
                    github_file = find_github_file_by_path(github_files, file_path)
                    if github_file:
                        content = github_file.get("content", "")
                
                # If no GitHub content, try to read local file
                if content is None:
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                    except Exception:
                        content = "Could not read file"
                
                if force_full_content:
                    codebase_context[file_path] = content
                    continue

                # Check if file should be truncated based on metadata
                metadata = file_metadata.get(file_path, {}) if file_metadata else {}
                is_truncated = metadata.get('truncated', False)
                description = metadata.get('description', '')
                
                if is_truncated and description:
                    # Use description + code gist for truncated files
                    # Get first 100 characters as gist
                    code_gist = content[:100] + "..." if len(content) > 100 else content
                    codebase_context[file_path] = f"{description}\n\nCode gist: {code_gist}"
                else:
                    # Use full content for non-truncated files
                    # Limit content size for API (3000 chars is fine as per user request)
                    if len(content) > 3000:
                        content = content[:3000] + "\n... [truncated]"
                    codebase_context[file_path] = content
            except Exception as e:
                codebase_context[file_path] = f"Could not read file: {str(e)}"
    
    return codebase_context

def create_comprehensive_analysis_prompt(state: CodeAnalysisState, codebase_context: Dict[str, str], file_metadata: Dict[str, Dict] = None) -> str:
    """Create a comprehensive prompt for AI review with full codebase context"""
    
    detected_issues = state.get("all_issues", [])
    discovered_files = state.get("discovered_files", {})
    
    # Format codebase for AI
    codebase_summary = []
    for file_path, content in codebase_context.items():
        codebase_summary.append(f"=== {file_path} ===\n{content}\n")
    
    # Format detected issues
    issues_summary = []
    for issue in detected_issues:
        issues_summary.append(f"""
ID: {issue.id}
Issue: {issue.title}
File: {issue.file_path}:{issue.line_number or 'N/A'}
Severity: {issue.severity}
Category: {issue.category}
Description: {issue.description}
Current Suggestion: {issue.suggestion}
""")
    
    prompt = f"""You are a Senior Code Quality Architect and Security Expert reviewing a complete codebase. 

CODEBASE CONTEXT:
{chr(10).join(codebase_summary)}

DETECTED ISSUES BY STATIC ANALYSIS:
{chr(10).join(issues_summary)}

PROJECT STRUCTURE:
- Total Files: {sum(len(files) for files in discovered_files.values())}
- Python Files: {len(discovered_files.get('python', []))}
- JavaScript Files: {len(discovered_files.get('javascript', []))}

YOUR TASK AS AI REVIEWER:
1. **COMPREHENSIVE ANALYSIS**: Review the entire codebase, not just detected issues
2. **CONTEXTUAL UNDERSTANDING**: Understand the project's purpose, architecture, and data flow
3. **ADDITIONAL ISSUE DETECTION**: Find issues that static analysis missed
4. **SEVERITY REASSESSMENT**: Re-evaluate severity based on business context
5. **ARCHITECTURAL REVIEW**: Identify design patterns, anti-patterns, and structural issues
6. **SECURITY DEEP DIVE**: Find security vulnerabilities beyond basic patterns
7. **PERFORMANCE ANALYSIS**: Identify bottlenecks and optimization opportunities
8. **MAINTAINABILITY ASSESSMENT**: Code quality, documentation, testability

CRITICAL JSON REQUIREMENTS:
1. Respond with ONLY valid JSON - no markdown, no explanations, no additional text
2. Ensure all strings are properly escaped and quoted
3. Ensure all objects and arrays are properly closed with }} and ]
4. Ensure all properties are separated by commas
5. Do not include any incomplete or truncated JSON
6. For each issue in "enhanced_issues", you MUST use the original ID from the "DETECTED ISSUES BY STATIC ANALYSIS" section. For "new_issues_found", generate a new unique ID in the format "category_NNN".

Example response format:
{{
  "executive_summary": "This codebase shows good modular structure but has several security and performance concerns that need immediate attention.",
  "architecture_analysis": {{
    "design_patterns": ["Factory Pattern", "Observer Pattern"],
    "anti_patterns": ["God Object", "Spaghetti Code"],
    "structure_assessment": "Well-organized with clear separation of concerns",
    "dependencies": "Minimal external dependencies, good isolation",
    "modularity_score": 8
  }},
  "enhanced_issues": [
    {{
      "id": "security_001",
      "title": "Hardcoded API Key Exposure",
      "category": "security",
      "severity": "critical",
      "file_path": "backend/main.py",
      "line_number": 15,
      "description": "API key is hardcoded in source code, creating security vulnerability",
      "code_snippet": "api_key = 'sk-1234567890abcdef'",
      "ai_analysis": "This exposes sensitive credentials in version control and production code",
      "business_impact": "High risk of data breach and unauthorized access",
      "fix_strategy": "Move to environment variables and use secure key management",
      "code_example": {{
        "before": "api_key = 'sk-1234567890abcdef'",
        "after": "api_key = os.getenv('API_KEY')"
      }},
      "prevention": "Use environment variables and secret management tools",
      "impact_score": 9.5
    }}
  ],
  "new_issues_found": [
    {{
      "id": "perf_001",
      "title": "Inefficient Database Query",
      "category": "performance",
      "severity": "medium",
      "file_path": "backend/services/db.py",
      "line_number": 42,
      "description": "N+1 query problem in user data fetching",
      "code_snippet": "for user in users: user.profile = get_profile(user.id)",
      "ai_analysis": "This creates multiple database queries instead of one optimized query",
      "business_impact": "Slower response times and increased database load",
      "fix_strategy": "Use eager loading or join queries to fetch all data at once",
      "code_example": {{
        "before": "for user in users: user.profile = get_profile(user.id)",
        "after": "users_with_profiles = get_users_with_profiles(users)"
      }},
      "prevention": "Always review database query patterns and use ORM optimization features",
      "impact_score": 7.0
    }}
  ],
  "false_positives": [],
  "recommendations": {{
    "immediate_actions": ["Fix hardcoded API key", "Add input validation"],
    "short_term": ["Implement proper error handling", "Add unit tests"],
    "long_term": ["Implement CI/CD pipeline", "Add monitoring"],
    "tools_suggested": ["ESLint", "SonarQube", "Snyk"],
    "best_practices": ["Code reviews", "Security scanning", "Performance monitoring"]
  }},
  "quality_metrics": {{
    "overall_score": 7.5,
    "security_score": 6.0,
    "maintainability_score": 8.0,
    "performance_score": 7.0,
    "test_coverage_assessment": "Estimated 60% coverage, needs improvement"
  }},
  "technical_debt": {{
    "level": "medium",
    "main_sources": ["Legacy code patterns", "Missing tests", "Hardcoded values"],
    "refactoring_priority": ["Security fixes", "Performance optimization", "Test coverage"]
  }}
}}

Your response:"""

    return prompt

def parse_ai_review_response(response_text: str) -> Dict[str, Any]:
    """Parse AI review response with robust error handling and JSON repair"""
    print(f"🔍 Raw AI response length: {len(response_text)} characters")
    print(f"🔍 First 200 chars: {response_text[:200]}")
    
    try:
        # Clean the response text
        cleaned_text = response_text.strip()
        
        # Remove any markdown code blocks if present
        if cleaned_text.startswith('```json'):
            cleaned_text = cleaned_text[7:]
        if cleaned_text.startswith('```'):
            cleaned_text = cleaned_text[3:]
        if cleaned_text.endswith('```'):
            cleaned_text = cleaned_text[:-3]
        
        cleaned_text = cleaned_text.strip()
        
        # Try to find JSON object boundaries more precisely
        start_idx = cleaned_text.find('{')
        end_idx = cleaned_text.rfind('}')
        
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            json_text = cleaned_text[start_idx:end_idx + 1]
            print(f"🔍 Extracted JSON length: {len(json_text)} characters")
            
            # Try to parse the JSON
            try:
                parsed = json.loads(json_text)
                print("✅ Successfully parsed AI response JSON")
                return parsed
            except json.JSONDecodeError as e:
                print(f"❌ JSON decode error: {e}")
                print(f"🔍 Attempting to repair JSON...")
                
                # Try to repair common JSON issues
                repaired_json = repair_json(json_text)
                if repaired_json:
                    try:
                        parsed = json.loads(repaired_json)
                        print("✅ Successfully parsed repaired JSON")
                        return parsed
                    except json.JSONDecodeError:
                        print("❌ JSON repair failed")
                else:
                    print("❌ Could not repair JSON")
                
                # If repair fails, try to extract partial data
                return extract_partial_ai_data(json_text)
        else:
            print("❌ Could not find valid JSON boundaries")
            raise ValueError("No valid JSON found in response")
            
    except Exception as e:
        print(f"❌ Error parsing AI response: {e}")
    
    # Fallback structure if parsing fails
    print("⚠️ Using fallback structure due to parsing failure")
    return {
        "executive_summary": "AI review parsing failed, using fallback analysis. The AI response was not in valid JSON format.",
        "enhanced_issues": [],
        "new_issues_found": [],
        "recommendations": {"immediate_actions": ["Review AI integration", "Check prompt formatting"]},
        "quality_metrics": {"overall_score": 5.0},
        "error": "Failed to parse AI response - likely due to malformed JSON"
    }

def repair_json(json_text: str) -> str:
    """Attempt to repair common JSON formatting issues"""
    try:
        # Fix common issues
        repaired = json_text
        
        # Attempt to fix invalid escape sequences by replacing single backslashes with double backslashes
        # This is a common issue when file paths are included in the JSON.
        # We use a negative lookbehind `(?<!\\)` to avoid replacing already-escaped backslashes.
        repaired = re.sub(r'(?<!\\)\\([^\/"bfnrt])', r'\\\\\1', repaired)

        # Fix missing commas between array elements
        repaired = re.sub(r'}\s*{', '},{', repaired)
        
        # Fix missing commas between object properties
        repaired = re.sub(r'"\s*\n\s*"', '",\n"', repaired)
        
        # Fix trailing commas
        repaired = re.sub(r',\s*}', '}', repaired)
        repaired = re.sub(r',\s*]', ']', repaired)
        
        # Try to fix incomplete strings by truncating at the error point
        # This is a simple approach - for production, you'd want more sophisticated repair
        return repaired
        
    except Exception as e:
        print(f"❌ JSON repair failed: {e}")
        return None

def extract_partial_ai_data(json_text: str) -> Dict[str, Any]:
    """Extract partial data from malformed JSON"""
    print("🔧 Attempting to extract partial data from malformed JSON...")
    
    try:
        # Try to extract executive summary
        exec_match = re.search(r'"executive_summary":\s*"([^"]*)"', json_text)
        executive_summary = exec_match.group(1) if exec_match else "Partial analysis - JSON parsing failed"
        
        # Try to extract some issues using regex
        enhanced_issues = []
        new_issues = []
        
        # Look for issue patterns in the text
        issue_patterns = re.findall(r'"title":\s*"([^"]*)"', json_text)
        for i, title in enumerate(issue_patterns[:10]):  # Limit to 10 issues
            if "enhanced" in title.lower() or "existing" in title.lower():
                enhanced_issues.append({
                    "id": f"partial_{i}",
                    "title": title,
                    "category": "style",
                    "severity": "medium",
                    "description": "Issue extracted from partial JSON parsing"
                })
            else:
                new_issues.append({
                    "id": f"partial_new_{i}",
                    "title": title,
                    "category": "style", 
                    "severity": "medium",
                    "description": "Issue extracted from partial JSON parsing"
                })
        
        return {
            "executive_summary": executive_summary,
            "enhanced_issues": enhanced_issues,
            "new_issues_found": new_issues,
            "recommendations": {"immediate_actions": ["Fix JSON parsing", "Review AI response format"]},
            "quality_metrics": {"overall_score": 6.0},
            "partial_data": True
        }
        
    except Exception as e:
        print(f"❌ Partial data extraction failed: {e}")
        return {
            "executive_summary": "Failed to extract any meaningful data from AI response",
            "enhanced_issues": [],
            "new_issues_found": [],
            "recommendations": {"immediate_actions": ["Critical: Fix AI response parsing"]},
            "quality_metrics": {"overall_score": 3.0},
            "error": "Complete parsing failure"
        }

def find_line_number_for_snippet(file_path: str, snippet: str, github_files: List[Dict] = None) -> int | None:
    """
    Finds the line number of a given code snippet in a file.
    Works with both local files and GitHub repository files.
    Returns the 1-based line number or None if not found.
    
    The function uses multiple strategies to find the best match:
    1. Exact multi-line match
    2. First line match
    3. Sliding window comparison for partial matches
    """
    print(f"\n[find_line_number] DEBUG: Looking for snippet in {file_path}")
    print(f"[find_line_number] Snippet: '{snippet}'")
    
    if not snippet or not file_path:
        print(f"[find_line_number] Empty snippet or file path")
        return None
    
    # Clean up the snippet
    clean_snippet = snippet.strip()
    if len(clean_snippet) < 3:  # Too short to be reliable
        print(f"[find_line_number] Snippet too short after cleaning: '{clean_snippet}'")
        return None
    
    # Get file content (either from GitHub or local file)
    lines = None
    
    # First check GitHub files
    if github_files:
        print(f"[find_line_number] Checking {len(github_files)} GitHub files")
        from backend.analyzers.github_helpers import find_github_file_by_path
        github_file = find_github_file_by_path(github_files, file_path)
        if github_file:
            print(f"[find_line_number] Found file in GitHub: {github_file.get('file_path')}")
            content = github_file.get("content", "")
            if content:
                lines = content.split('\n')
                print(f"[find_line_number] Got content from GitHub file: {len(lines)} lines")
            else:
                print(f"[find_line_number] No content in GitHub file")
        else:
            print(f"[find_line_number] File not found in GitHub files")
    
    # If not found in GitHub files, try local file
    if lines is None:
        print(f"[find_line_number] Trying to read local file: {file_path}")
        if not os.path.exists(file_path):
            print(f"[find_line_number] File does not exist locally: {file_path}")
            return None
            
        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()
                # Strip newlines from readlines output
                lines = [line.rstrip('\r\n') for line in lines]
                print(f"[find_line_number] Read {len(lines)} lines from local file")
        except Exception as e:
            print(f"⚠️  Could not read file {file_path} to verify line number: {e}")
            return None
    
    try:
        # Split snippet into lines and clean them
        snippet_lines = [line.strip() for line in clean_snippet.split('\n') if line.strip()]
        if not snippet_lines:
            print(f"[find_line_number] No valid lines in snippet after cleaning: '{clean_snippet}'")
            return None
        
        print(f"[find_line_number] Searching for snippet with {len(snippet_lines)} lines. First line: '{snippet_lines[0]}'")
        
        # Strategy 1: Try to find exact match for first line (fastest approach)
        first_line = snippet_lines[0]
        for i, line in enumerate(lines):
            if isinstance(line, str) and first_line in line.strip():
                # If it's a multi-line snippet, verify following lines also match
                if len(snippet_lines) > 1 and i + len(snippet_lines) <= len(lines):
                    all_lines_match = True
                    for j, snippet_line in enumerate(snippet_lines[1:], 1):
                        if snippet_line not in lines[i+j].strip():
                            all_lines_match = False
                            break
                    if all_lines_match:
                        print(f"[find_line_number] Successfully found line {i+1} for snippet: '{first_line}'")
                        return i + 1
                else:
                    # Single line snippet
                    print(f"[find_line_number] Successfully found line {i+1} for snippet: '{first_line}'")
                    return i + 1
        
        # Strategy 2: Try fuzzy matching with sliding window for multi-line snippets
        if len(snippet_lines) > 1:
            print(f"[find_line_number] Trying fuzzy matching for multi-line snippet")
            snippet_text = ' '.join(snippet_lines).lower()
            for i in range(len(lines) - len(snippet_lines) + 1):
                window_text = ' '.join(lines[i:i+len(snippet_lines)]).lower()
                # Check if there's significant overlap between the snippet and window
                if len(snippet_text) > 0 and len(window_text) > 0:
                    # Simplistic fuzzy match - check if 60% of snippet content is in the window
                    common_chars = sum(1 for c in snippet_text if c in window_text)
                    match_percentage = common_chars / len(snippet_text)
                    if match_percentage > 0.6:
                        print(f"[find_line_number] Found fuzzy match at line {i+1} for multi-line snippet (match: {match_percentage:.2f})")
                        return i + 1
                    elif match_percentage > 0.4:
                        print(f"[find_line_number] Close fuzzy match at line {i+1} (match: {match_percentage:.2f}), but below threshold")
        
        # Strategy 3: Last resort - try to find any distinctive substring
        # Look for distinctive parts that are less likely to be common
        distinctive_parts = []
        for line in snippet_lines:
            if len(line) > 20 and ('(' in line or '=' in line or ':' in line):
                distinctive_parts.append(line)
        
        if distinctive_parts:
            print(f"[find_line_number] Trying distinctive part matching with {len(distinctive_parts)} candidate parts")
            for part in distinctive_parts:
                print(f"[find_line_number] Looking for distinctive part: '{part[:30]}...'")
                for i, line in enumerate(lines):
                    if part in line:
                        print(f"[find_line_number] Found distinctive part match at line {i+1}")
                        return i + 1
        
        # Strategy 4: Handle placeholder/example snippets that don't exist verbatim
        # This specifically targets AI-generated examples like the ones in your logs
        print(f"[find_line_number] Trying pattern matching for AI-generated examples")
        
        # Look for key patterns like function calls and variable assignments
        if "subprocess.run" in clean_snippet and "git diff" in clean_snippet:
            print(f"[find_line_number] Looking for subprocess with git diff")
            for i, line in enumerate(lines):
                if "subprocess.run" in line and "git" in line:
                    print(f"[find_line_number] Found subprocess with git pattern at line {i+1}")
                    return i + 1
        
        if "openai.api_key" in clean_snippet and ("sk-" in clean_snippet or "XXXX" in clean_snippet):
            print(f"[find_line_number] Looking for OpenAI API key pattern")
            for i, line in enumerate(lines):
                if "openai.api_key" in line:
                    print(f"[find_line_number] Found OpenAI API key at line {i+1}")
                    return i + 1
        
        if "for" in clean_snippet and "openai" in clean_snippet and ("Completion" in clean_snippet or "create" in clean_snippet):
            print(f"[find_line_number] Looking for OpenAI completion in loop")
            for i, line in enumerate(lines):
                if "for" in line and i+1 < len(lines) and "openai" in lines[i+1]:
                    print(f"[find_line_number] Found OpenAI completion in loop at line {i+1}")
                    return i + 1
        
        if "def process_review" in clean_snippet:
            print(f"[find_line_number] Looking for process_review function definition")
            for i, line in enumerate(lines):
                if "def process_review" in line:
                    print(f"[find_line_number] Found process_review definition at line {i+1}")
                    return i + 1
        
        # Fall back to more general function or class name search
        function_match = re.search(r"def\s+(\w+)", clean_snippet)
        if function_match:
            function_name = function_match.group(1)
            print(f"[find_line_number] Looking for function definition: '{function_name}'")
            for i, line in enumerate(lines):
                if f"def {function_name}" in line:
                    print(f"[find_line_number] Found function definition at line {i+1}")
                    return i + 1
        
        print(f"[find_line_number] No match found for snippet in file after trying all strategies")
        return None # Snippet not found
    except Exception as e:
        print(f"⚠️  Error finding line number for snippet in {file_path}: {e}")
        return None

def convert_ai_issues_to_code_issues(ai_issues: List[Dict], issue_type: str = "enhanced", github_files: List[Dict] = None) -> List[CodeIssue]:
    """Convert AI-generated issues to CodeIssue objects with line number verification"""
    code_issues = []
    
    for i, ai_issue in enumerate(ai_issues):
        try:
            # Map AI categories to our enum
            category_map = {
                "security": IssueCategory.SECURITY,
                "performance": IssueCategory.PERFORMANCE,
                "complexity": IssueCategory.COMPLEXITY,
                "duplication": IssueCategory.DUPLICATION,
                "testing": IssueCategory.TESTING,
                "documentation": IssueCategory.DOCUMENTATION,
                "style": IssueCategory.STYLE
            }
            
            severity_map = {
                "critical": IssueSeverity.CRITICAL,
                "high": IssueSeverity.HIGH,
                "medium": IssueSeverity.MEDIUM,
                "low": IssueSeverity.LOW
            }
            
            suggestion = ai_issue.get("fix_strategy", "No specific fix suggested.")
            
            context_parts = []
            if ai_issue.get("ai_analysis"):
                context_parts.append(f"🤖 AI Analysis: {ai_issue['ai_analysis']}")
            if ai_issue.get("business_impact"):
                context_parts.append(f"💼 Business Impact: {ai_issue['business_impact']}")
            if ai_issue.get("code_example"):
                example = ai_issue["code_example"]
                context_parts.append(f"📝 Code Example:\n  Before: {example.get('before', 'N/A')}\n  After: {example.get('after', 'N/A')}")
            if ai_issue.get("prevention"):
                context_parts.append(f"🛡️ Prevention: {ai_issue['prevention']}")
            
            ai_review_context = "\n\n".join(context_parts) if context_parts else None
            
            code_snippet = ai_issue.get("code_snippet", "")
            if isinstance(code_snippet, list):
                code_snippet = "\n".join(str(item) for item in code_snippet)
            elif not isinstance(code_snippet, str):
                code_snippet = str(code_snippet) if code_snippet else ""

            file_path = ai_issue.get("file_path", "unknown")
            
            # --- LINE NUMBER VERIFICATION LOGIC ---
            verified_line_number = find_line_number_for_snippet(file_path, code_snippet, github_files)
            
            if verified_line_number is None:
                # If snippet not found, explicitly set line number to None
                line_number = None
            else:
                line_number = verified_line_number

            code_issue = CodeIssue(
                id=ai_issue.get("id", f"ai_{issue_type}_{i}"),
                category=category_map.get(ai_issue.get("category", "style").lower(), IssueCategory.STYLE),
                severity=severity_map.get(ai_issue.get("severity", "medium").lower(), IssueSeverity.MEDIUM),
                title=ai_issue.get("title", "AI-Detected Issue"),
                description=ai_issue.get("description", "Issue detected by AI review"),
                file_path=file_path,
                line_number=line_number,
                code_snippet=code_snippet,
                suggestion=suggestion,
                impact_score=float(ai_issue.get("impact_score", 5.0)),
                ai_review_context=ai_review_context
            )
            
            code_issues.append(code_issue)
            
        except Exception as e:
            print(f"Error converting AI issue {i}: {e}")
            continue
    
    return code_issues

def ai_review_agent(state: CodeAnalysisState) -> CodeAnalysisState:
    """Comprehensive AI review agent that curates all results with full codebase context"""
    
    model_choice = state.get("model_choice", "gemini")
    llm_model = get_llm_model(model_choice)

    if not llm_model:
        print(f"⚠️ {model_choice.capitalize()} model not available, skipping AI review")
        return {**state, "current_step": "ai_review_skipped"}
    
    print("🤖 Starting comprehensive AI review with intelligent truncation...")
    
    try:
        # Read entire codebase for context with intelligent truncation
        discovered_files = state.get("discovered_files", {})
        file_metadata = state.get("file_metadata", {})
        github_files = state.get("github_files", [])  # Get GitHub files if present
        
        total_files = sum(len(files) for files in discovered_files.values())
        force_full_content = total_files <= 5

        if force_full_content:
            print("🔍 Fewer than 6 files detected. Reading full file contents for AI review.")

        # Count truncated vs full files
        truncated_count = 0
        full_count = 0
        if not force_full_content:
            for file_path in sum(discovered_files.values(), []):
                metadata = file_metadata.get(file_path, {})
                if metadata.get('truncated', False):
                    truncated_count += 1
                else:
                    full_count += 1
        else:
            full_count = total_files

        print(f"📊 File processing: {truncated_count} truncated (description only), {full_count} full content")
        
        codebase_context = read_codebase_context(discovered_files, file_metadata, github_files, force_full_content=force_full_content)
        
        # Create comprehensive analysis prompt
        analysis_prompt = create_comprehensive_analysis_prompt(state, codebase_context, file_metadata)
        
        print("🧠 Sending codebase to AI for comprehensive review...")
        
        # Get AI review with retry mechanism
        ai_review = None
        max_retries = 2
        
        for attempt in range(max_retries):
            try:
                ai_response = llm_model.generate_content(analysis_prompt)
                ai_review = parse_ai_review_response(ai_response.text)
                
                # Check if parsing was successful
                if not ai_review.get("error") and not ai_review.get("partial_data"):
                    print("✅ AI review completed successfully")
                    break
                elif attempt < max_retries - 1:
                    print(f"🔄 Retrying AI review (attempt {attempt + 2}/{max_retries})...")
                    # Add a more specific prompt for retry
                    retry_prompt = f"{analysis_prompt}\n\nIMPORTANT: The previous response had JSON formatting issues. Please ensure your response is valid JSON with proper syntax."
                    ai_response = llm_model.generate_content(retry_prompt)
                    ai_review = parse_ai_review_response(ai_response.text)
                else:
                    print("⚠️ All retry attempts failed, using best available data")
                    break
                    
            except Exception as e:
                print(f"❌ AI review attempt {attempt + 1} failed: {e}")
                if attempt == max_retries - 1:
                    # Final fallback
                    ai_review = {
                        "executive_summary": "AI review failed after multiple attempts",
                        "enhanced_issues": [],
                        "new_issues_found": [],
                        "recommendations": {"immediate_actions": ["Critical: AI review system needs attention"]},
                        "quality_metrics": {"overall_score": 3.0},
                        "error": f"AI review failed: {str(e)}"
                    }
        
        # Get GitHub files from state if available
        github_files = state.get("github_files", [])
        
        # Convert AI issues to CodeIssue objects
        enhanced_issues = convert_ai_issues_to_code_issues(
            ai_review.get("enhanced_issues", []), "enhanced", github_files
        )
        
        new_issues = convert_ai_issues_to_code_issues(
            ai_review.get("new_issues_found", []), "new", github_files
        )
        
        # De-duplicate and merge issues
        existing_issues = state.get("all_issues", [])
        final_issues = {issue.id: issue for issue in existing_issues}

        for issue in enhanced_issues:
            if issue.id in final_issues:
                # Update existing issue with AI enhancements
                final_issues[issue.id].suggestion = issue.suggestion
                final_issues[issue.id].impact_score = issue.impact_score
                final_issues[issue.id].ai_review_context = issue.ai_review_context
                # AI can also reassess severity and description
                final_issues[issue.id].severity = issue.severity
                final_issues[issue.id].description = issue.description
                final_issues[issue.id].title = issue.title
            else:
                # If the AI-enhanced issue's ID is not in existing issues, it's a new issue
                final_issues[issue.id] = issue

        for issue in new_issues:
            # Add new issues found by AI, ensuring no ID collision
            if issue.id not in final_issues:
                final_issues[issue.id] = issue
            else:
                # Handle rare case of ID collision from new issues
                print(f"⚠️ Warning: ID collision for new issue '{issue.id}'. Discarding.")
        
        state["all_issues"] = list(final_issues.values())
        state["ai_review"] = ai_review
        state["current_step"] = "ai_review_complete"
        
        return state
        
    except Exception as e:
        print(f"❌ AI review failed: {e}")
        return {
            **state,
            "errors": state.get("errors", []) + [f"AI review failed: {str(e)}"],
            "current_step": "ai_review_failed"
        }