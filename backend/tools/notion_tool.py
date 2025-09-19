import os
from typing import Dict, List, Any
from notion_client import Client
from notion_client.errors import APIResponseError

def push_to_notion(report: Dict[str, Any]) -> bool:
    """
    Pushes a structured code review report into Notion.

    Args:
        report: Dictionary containing the code review results with structure:
            {
                "file": "path/to/file.py",
                "issues": ["Issue 1", "Issue 2"],
                "fixes": {"issue1": "suggestion1", "issue2": "suggestion2"},
                "code": "code snippet or comprehensive report",
                "language": "python",  # optional, defaults to "python"
                "severity": "high",  # optional
                "summary": "Brief summary"  # optional
            }

    Returns:
        bool: True if successful, False otherwise

    Raises:
        ValueError: If NOTION_TOKEN or NOTION_PAGE_ID environment variables are not set
        APIResponseError: If Notion API call fails
    """
    notion_token = os.getenv("NOTION_TOKEN")
    parent_page = os.getenv("NOTION_PAGE_ID")

    if not notion_token or not parent_page:
        raise ValueError("NOTION_TOKEN and NOTION_PAGE_ID must be set in environment variables")

    client = Client(auth=notion_token)

    # Extract report data with defaults
    file_name = report.get("file", "Unknown file")
    issues = report.get("issues", [])
    fixes = report.get("fixes", {})
    code = report.get("code", "")
    language = report.get("language", "python")
    severity = report.get("severity", "medium")
    summary = report.get("summary", "")

    children_blocks = []

    # Page title and summary
    title_content = f"Code Review: {file_name}"
    if summary:
        title_content += f" - {summary}"

    children_blocks.append({
        "object": "block",
        "type": "heading_1",
        "heading_1": {
            "rich_text": [{"type": "text", "text": {"content": title_content}}]
        }
    })

    # Severity indicator
    severity_emoji = {
        "critical": "",
        "high": "",
        "medium": "",
        "low": ""
    }.get(severity.lower(), "ℹ")

    children_blocks.append({
        "object": "block",
        "type": "paragraph",
        "paragraph": {
            "rich_text": [
                {"type": "text", "text": {"content": f"{severity_emoji} Severity: {severity.upper()}"}}
            ]
        }
    })

    # Issues section
    if issues:
        children_blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Key Issues"}}]}
        })

        for issue in issues:
            children_blocks.append({
                "object": "block",
                "type": "bulleted_list_item",
                "bulleted_list_item": {
                    "rich_text": [{"type": "text", "text": {"content": issue}}]
                }
            })

    # Fixes section
    if fixes:
        children_blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Recommended Actions"}}]}
        })

        for category, actions in fixes.items():
            if isinstance(actions, list):
                children_blocks.append({
                    "object": "block",
                    "type": "heading_3",
                    "heading_3": {"rich_text": [{"type": "text", "text": {"content": category}}]}
                })

                for action in actions:
                    children_blocks.append({
                        "object": "block",
                        "type": "bulleted_list_item",
                        "bulleted_list_item": {
                            "rich_text": [{"type": "text", "text": {"content": action}}]
                        }
                    })
            else:
                # Handle single fix items
                content_text = f"{category}: {actions}"
                children_blocks.append({
                    "object": "block",
                    "type": "bulleted_list_item",
                    "bulleted_list_item": {
                        "rich_text": [{"type": "text", "text": {"content": content_text}}]
                    }
                })

    # Comprehensive report section (if it's a detailed report)
    if code and len(code) > 500:  # If code content is long, treat it as comprehensive report
        children_blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Comprehensive Analysis Report"}}]}
        })

        # Check if the code appears to be a JSON structure (AI generated report)
        if code.strip().startswith('[') and code.strip().endswith(']'):
            try:
                import json
                # Try to parse as JSON array of blocks
                json_blocks = json.loads(code)
                if isinstance(json_blocks, list):
                    # Successfully parsed JSON array, add blocks directly
                    print(f" Processing {len(json_blocks)} JSON blocks for Notion")
                    for block in json_blocks:
                        # Validate basic structure of block before adding
                        if isinstance(block, dict) and "type" in block and "object" in block:
                            # Skip table blocks entirely as they often cause validation issues
                            if block.get("type") == "table":
                                print(f" Skipping table block to avoid validation issues")
                                continue
                            
                            # Check for rich_text content exceeding 2000 chars and split if needed
                            for field_name in ["paragraph", "bulleted_list_item", "heading_1", "heading_2", "heading_3"]:
                                if field_name in block:
                                    field = block[field_name]
                                    if "rich_text" in field and isinstance(field["rich_text"], list):
                                        for i, text_item in enumerate(field["rich_text"]):
                                            if "text" in text_item and "content" in text_item["text"]:
                                                content = text_item["text"]["content"]
                                                # If content is too long, truncate it to avoid API errors
                                                if len(content) > 1990:  # Leave small margin
                                                    field["rich_text"][i]["text"]["content"] = content[:1990]
                            
                            # Additional validation: ensure block has required structure
                            block_type = block.get("type")
                            if block_type == "divider":
                                # Divider blocks just need the divider key
                                if "divider" not in block:
                                    block["divider"] = {}
                                children_blocks.append(block)
                            elif block_type and block_type in block and "rich_text" in block[block_type]:
                                # Regular text blocks
                                children_blocks.append(block)
                            else:
                                print(f" Skipping invalid block structure: {block_type}")
                    
                    # No need to process further
                    print(" Processed JSON blocks for Notion")
                    
                else:
                    # Not a list, fall back to text processing
                    raise ValueError("Not a valid JSON blocks array")
            except Exception as e:
                print(f" Could not parse JSON blocks: {e}. Falling back to text processing.")
                # Fall back to processing as regular text paragraphs
                paragraphs = code.split('\n\n')
                for paragraph in paragraphs[:20]:  # Limit to first 20 paragraphs to avoid API limits
                    if paragraph.strip():
                        # Regular paragraph
                        children_blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {"rich_text": [{"type": "text", "text": {"content": paragraph[:1990]}}]}
                        })
        else:
            # Process as regular markdown content
            paragraphs = code.split('\n\n')
            for paragraph in paragraphs[:20]:  # Limit to first 20 paragraphs to avoid API limits
                if paragraph.strip():
                    # Handle markdown-style headers
                    if paragraph.startswith('#'):
                        level = paragraph.count('#')
                        if level <= 3:  # Only support h1, h2, h3
                            header_type = f"heading_{level}"
                            header_text = paragraph.lstrip('#').strip()
                            children_blocks.append({
                                "object": "block",
                                "type": header_type,
                                header_type: {"rich_text": [{"type": "text", "text": {"content": header_text[:1990]}}]}
                            })
                        else:
                            # Treat as regular paragraph
                            children_blocks.append({
                                "object": "block",
                                "type": "paragraph",
                                "paragraph": {"rich_text": [{"type": "text", "text": {"content": paragraph[:1990]}}]}
                            })
                    elif paragraph.startswith('- ') or paragraph.startswith('* '):
                        # Handle bullet points
                        bullets = paragraph.split('\n')
                        for bullet in bullets:
                            if bullet.strip():
                                children_blocks.append({
                                    "object": "block",
                                    "type": "bulleted_list_item",
                                    "bulleted_list_item": {
                                        "rich_text": [{"type": "text", "text": {"content": bullet.lstrip('- ').lstrip('* ').strip()[:1990]}}]
                                    }
                                })
                    else:
                        # Regular paragraph
                        children_blocks.append({
                            "object": "block",
                            "type": "paragraph",
                            "paragraph": {"rich_text": [{"type": "text", "text": {"content": paragraph[:1990]}}]}
                        })
    elif code:
        # Code block for shorter content
        children_blocks.append({
            "object": "block",
            "type": "heading_2",
            "heading_2": {"rich_text": [{"type": "text", "text": {"content": "Code Analysis"}}]}
        })

        # If the code is JSON and marked as such, try to parse it
        if language.lower() == "json" and code.strip().startswith('[') and code.strip().endswith(']'):
            try:
                import json
                json_blocks = json.loads(code)
                if isinstance(json_blocks, list):
                    # Process JSON blocks directly - already handled above
                    for block in json_blocks:
                        if isinstance(block, dict) and "type" in block and "object" in block:
                            # Check for rich_text content exceeding 2000 chars and truncate if needed
                            for field_name in ["paragraph", "bulleted_list_item", "heading_1", "heading_2", "heading_3"]:
                                if field_name in block:
                                    field = block[field_name]
                                    if "rich_text" in field and isinstance(field["rich_text"], list):
                                        for i, text_item in enumerate(field["rich_text"]):
                                            if "text" in text_item and "content" in text_item["text"]:
                                                content = text_item["text"]["content"]
                                                if len(content) > 1990:
                                                    field["rich_text"][i]["text"]["content"] = content[:1990]
                            
                            children_blocks.append(block)
                    return
            except:
                # Fall back to treating as raw code
                pass
                
        # Default handling for non-JSON or failed JSON parsing
        children_blocks.append({
            "object": "block",
            "type": "code",
            "code": {
                "rich_text": [{"type": "text", "text": {"content": code[:2000] if len(code) > 2000 else code}}],
                "language": language
            }
        })

    # Create the page in Notion
    try:
        client.pages.create(
            parent={"page_id": parent_page},
            properties={
                "title": {
                    "title": [{"type": "text", "text": {"content": title_content}}]
                }
            },
            children=children_blocks
        )
        print(f" Successfully created Notion page for: {file_name}")
        return True
    except APIResponseError as e:
        print(f" Failed to create Notion page: {e}")
        return False
    except Exception as e:
        print(f" Unexpected error creating Notion page: {e}")
        return False

def push_analysis_results_to_notion(analysis_results: Dict[str, Any]) -> bool:
    """
    Pushes complete analysis results to Notion, creating multiple pages if needed.

    Args:
        analysis_results: Complete analysis results from the workflow

    Returns:
        bool: True if all reports were pushed successfully
    """
    success_count = 0
    total_count = 0

    # Extract issues and create individual reports
    all_issues = analysis_results.get("all_issues", [])

    # Group issues by file
    issues_by_file = {}
    for issue in all_issues:
        file_path = issue.get("file_path", "unknown_file")
        if file_path not in issues_by_file:
            issues_by_file[file_path] = []
        issues_by_file[file_path].append(issue)

    # Create a report for each file with issues
    for file_path, issues in issues_by_file.items():
        total_count += 1

        # Extract issue descriptions and fixes
        issue_descriptions = []
        fixes = {}

        for issue in issues:
            description = issue.get("description", "")
            issue_key = f"Issue {len(issue_descriptions) + 1}"
            issue_descriptions.append(description)

            # Try to get fix suggestion from issue
            fix = issue.get("fix_suggestion", "")
            if fix:
                fixes[issue_key] = fix

        # Determine severity based on highest severity issue
        severities = [issue.get("severity", "low") for issue in issues]
        severity_hierarchy = {"low": 1, "medium": 2, "high": 3, "critical": 4}
        max_severity = max(severities, key=lambda s: severity_hierarchy.get(s.lower(), 0))
        severity = max_severity if max_severity else "medium"

        # Create report dictionary
        report = {
            "file": file_path,
            "issues": issue_descriptions,
            "fixes": fixes,
            "code": "",  # Could be populated with actual code snippets
            "language": "python" if file_path.endswith(".py") else "javascript",
            "severity": severity,
            "summary": f"Found {len(issues)} issue(s)"
        }

        # Push to Notion
        if push_to_notion(report):
            success_count += 1

    print(f" Notion reporting complete: {success_count}/{total_count} reports created")
    return success_count == total_count
