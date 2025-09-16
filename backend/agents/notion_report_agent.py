from .state_schema import CodeAnalysisState
from backend.tools.notion_tool import push_to_notion
from backend.services.llm_service import get_llm_model
from typing import Dict, Any

def generate_comprehensive_report(state: CodeAnalysisState) -> Dict[str, Any]:
    """Generate a comprehensive, developer-friendly report using AI"""
    
    ai_review = state.get("ai_review", {})
    all_issues = state.get("all_issues", [])
    discovered_files = state.get("discovered_files", {})
    # Check if we need to enforce brevity (used by retry mechanism)
    enforce_brevity = state.get("enforce_brevity", False)
    
    # Get the target path for the report title
    target_path = state.get("target_path", "unknown")
    if target_path == ".":
        target_path = "current directory"
    
    # Prepare context for LLM
    issues_summary = []
    for issue in all_issues[:10]:  # Limit to top 10 issues
        issues_summary.append({
            "title": getattr(issue, 'title', 'Unknown Issue'),
            "severity": getattr(issue, 'severity', 'medium'),
            "description": getattr(issue, 'description', ''),
            "file_path": getattr(issue, 'file_path', ''),
            "suggestion": getattr(issue, 'suggestion', '')
        })
    
    # Create comprehensive report prompt with brevity constraints based on whether we need stricter limits
    brevity_note = ""
    
    if state.get("enforce_brevity", False):
        brevity_note = """
⚠️ CRITICAL: Previous attempt exceeded Notion's 2000 character limit. For this retry:
1. Keep content extremely brief and focused 
2. Ensure NO single rich_text content field exceeds 1500 characters (Notion limit is 2000)
3. Split any long text across multiple blocks
4. Focus only on top 2-3 issues with minimal explanation
5. Use only essential sections (skip some if needed)
6. Use shorter sentences and fewer bullet points
"""

    report_prompt = f"""You are a senior software architect creating a concise, developer-friendly code review report for Notion.

{brevity_note}
Generate the report as a JSON array of Notion block objects for proper API rendering. Ensure:

- Output is valid JSON: Array of block objects (e.g., {{"object": "block", "type": "heading_1", "heading_1": {{"rich_text": [{{"type": "text", "text": {{"content": "Text"}}}}]}}}}).
- CRITICAL REQUIREMENT: Each individual "content" field MUST be less than 2000 characters (preferably under 1500)
- IMPORTANT: For longer text, split into multiple consecutive blocks of the same type
- Use block types: heading_1, heading_2, paragraph, table, code (specify 'language'), bulleted_list_item, divider.
- Use bold/italic via annotations for clarity (e.g., {{'annotations': {{'bold': true}}}}).
- Explain top issues, suggest fixes, prioritize by severity (Critical, High, Medium, Low).
- Keep it visually appealing and actionable.

**Analysis Target:** {target_path}
**Files Analyzed:** {sum(len(files) for files in discovered_files.values())}
**Languages Detected:** {', '.join(discovered_files.keys())}
**Total Issues Found:** {len(all_issues)}
**AI Review Summary:** {ai_review.get('executive_summary', 'No summary')[:100]}
**Issues (top 3):** {chr(10).join(["- " + issue['title'] + " (" + issue['severity'] + ")" for issue in issues_summary[:3]])}

Structure as JSON array:

1. Heading 1: 📄 Report - {target_path}
   - Subtext: *AI-assisted*

2. Divider

3. Heading 2: Summary
   - Paragraph: 1-sentence overview.
   - Table: Metrics (Files, Languages, Issues, Quality/10).

4. Divider

5. Heading 2: Key Issues
   - Table: Top 3 issues (Priority, Title, Severity (🔴 Critical, 🟠 High, 🟡 Medium), Impact, Fix Effort).

6. Divider

7. Heading 2: Fixes
   - Bulleted list: Top issue fixes (Problem, Fix, Benefit).

8. Divider

9. Paragraph: *Generated: [Current Date]*

Output ONLY the JSON array."""
    # Get LLM to generate comprehensive report
    llm_model = get_llm_model(state.get("model_choice", "gemini"))
    
    if llm_model:
        try:
            print("🤖 Generating comprehensive developer-friendly report...")
            response = llm_model.generate_content(report_prompt)
            comprehensive_report = response.text
            print("✅ Comprehensive report generated")
        except Exception as e:
            print(f"❌ Failed to generate comprehensive report: {e}")
            comprehensive_report = f"Error generating comprehensive report: {e}"
    else:
        comprehensive_report = "LLM model not available for report generation"
    
    return {
        "file": target_path,
        "issues": [f"Found {len(all_issues)} issues across {sum(len(files) for files in discovered_files.values())} files"],
        "fixes": {
            "Critical Issues": ai_review.get('recommendations', {}).get('immediate_actions', []),
            "General Improvements": ["Review code quality metrics", "Implement suggested fixes", "Follow best practices"]
        },
        "code": "",  # Will be populated from actual code snippets if available
        "language": "python",  # Default
        "severity": "high" if len(all_issues) > 5 else "medium",
        "summary": ai_review.get('executive_summary', f'Analysis of {target_path}'),
        "comprehensive_report": comprehensive_report
    }

def generate_report_with_retry(state: CodeAnalysisState, max_retries: int = 3, enforce_brevity: bool = False) -> Dict[str, Any]:
    """
    Generate a comprehensive report with retries if it fails due to length constraints.
    
    Args:
        state: The code analysis state
        max_retries: Maximum number of retry attempts
        enforce_brevity: If True, specifically instruct the model to make the report very brief
        
    Returns:
        Dictionary containing the report data
    """
    retries = 0
    
    while retries < max_retries:
        try:
            # Generate the report
            report_data = generate_comprehensive_report(state)
            
            # Create the main report object to test
            main_report = {
                "file": report_data["file"],
                "issues": report_data["issues"],
                "fixes": report_data["fixes"],
                "code": report_data["comprehensive_report"],
                "language": "markdown",
                "severity": report_data["severity"],
                "summary": report_data["summary"]
            }
            
            # If we're on a retry, check that no single text block exceeds the Notion limit
            if enforce_brevity:
                # Simple check for long text content (actual validation happens in push_to_notion)
                content = report_data["comprehensive_report"]
                # Look for long JSON text blocks that might exceed Notion's 2000 char limit
                if '"content":' in content and len(content) > 1500:
                    print(f"🔄 Report may still be too long ({len(content)} chars). Retrying with stricter brevity...")
                    # Force a retry with more aggressive brevity constraints
                    raise ValueError("Content appears to exceed Notion limits")
            
            return report_data
            
        except Exception as e:
            retries += 1
            if retries >= max_retries:
                print(f"⚠️ Maximum retries reached ({max_retries}). Using simplified report.")
                # Return a simple fallback report if all retries fail
                target_path = state.get("target_path", "unknown")
                all_issues = state.get("all_issues", [])
                discovered_files = state.get("discovered_files", {})
                
                return {
                    "file": target_path,
                    "issues": [f"Found {len(all_issues)} issues across {sum(len(files) for files in discovered_files.values())} files"],
                    "fixes": {"Critical Issues": [], "General Improvements": ["Review code issues"]},
                    "code": "**Simplified Report**\n\nThe full report exceeded Notion character limits. Please check CLI output for complete details.",
                    "language": "markdown",
                    "severity": "medium",
                    "summary": f"Analysis of {target_path} (simplified due to content length constraints)"
                }
            else:
                print(f"⚠️ Report generation issue (likely too long). Retry {retries}/{max_retries} with brevity constraints...")
                # Toggle brevity flag on for the next attempt
                enforce_brevity = True
                
                # We'll continue the loop with brevity enforced
    
    # Should never reach here due to the return in the loop, but as a fallback
    return {"error": "Failed to generate report after multiple attempts"}

def notion_report_agent(state: CodeAnalysisState) -> CodeAnalysisState:
    """
    Agent that pushes comprehensive analysis results to Notion.
    """
    if not state.get("notion_reporting_enabled", False):
        print("📝 Notion reporting not enabled, skipping...")
        return state

    print("📝 Generating comprehensive report and pushing to Notion...")

    try:
        # Generate report with automatic retry for length issues
        report_data = generate_report_with_retry(state)
        
        # Create the main comprehensive report page
        main_report = {
            "file": report_data["file"],
            "issues": report_data["issues"],
            "fixes": report_data["fixes"],
            "code": report_data["comprehensive_report"],  # Use the comprehensive report as code content
            "language": "json",  # Use JSON to help Notion interpret the blocks structure
            "severity": report_data["severity"],
            "summary": report_data["summary"]
        }
        
        # Push main report to Notion
        success = push_to_notion(main_report)
        
        # If failed due to content length, retry with enforced brevity
        if not success:
            # Check if the last error message contains "2000" which likely indicates a length error
            last_error = state.get("errors", [""])[-1] if state.get("errors") else ""
            if "2000" in last_error or "length" in last_error.lower():
                print("🔄 Report too long for Notion. Retrying with strict character limits...")
                # Update state to enforce brevity in next report generation
                state["enforce_brevity"] = True
                report_data = generate_report_with_retry(state, enforce_brevity=True)
                
                # Update report with briefer content
                main_report["code"] = report_data["comprehensive_report"]
                main_report["summary"] = report_data["summary"] + " (brevity enforced)"
                
                # Try pushing again
                success = push_to_notion(main_report)
        
        if success:
            print("✅ Successfully pushed comprehensive report to Notion")
            state["current_step"] = "notion_report_complete"
        else:
            print("❌ Failed to push comprehensive report to Notion")
            if "errors" not in state:
                state["errors"] = []
            state["errors"].append("Failed to push comprehensive report to Notion")
            state["current_step"] = "notion_report_failed"

    except Exception as e:
        error_msg = f"Error in Notion reporting: {str(e)}"
        print(f"❌ {error_msg}")
        state["errors"].append(error_msg)
        state["current_step"] = "notion_report_error"

    return state