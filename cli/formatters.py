from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.progress import Progress
from backend.models.analysis_models import AnalysisResult, ChatResponse, IssueSeverity

console = Console()

def format_analysis_result(result: AnalysisResult, show_insights: bool = False) -> str:
    """Format analysis result for CLI display"""
    
    # Summary panel
    summary_text = f"""
📊 Analysis Summary
• Files analyzed: {result.total_files}
• Total lines: {result.total_lines:,}
• Issues found: {result.summary['total_issues']}
• Analysis time: {result.analysis_duration:.2f}s
• Languages: {', '.join(result.summary.get('languages_detected', []))}
"""
    
    console.print(Panel(summary_text, title="📈 Code Analysis Results", border_style="blue"))
    
    # Issues by severity
    if result.issues:
        severity_table = Table(title="🚨 Issues by Severity")
        severity_table.add_column("Severity", style="bold")
        severity_table.add_column("Count", justify="right")
        severity_table.add_column("Percentage", justify="right")
        
        total_issues = len(result.issues)
        severity_counts = result.summary.get('severity_breakdown', {})
        
        severity_colors = {
            'critical': 'red',
            'high': 'orange3',
            'medium': 'yellow',
            'low': 'green'
        }
        
        for severity in ['critical', 'high', 'medium', 'low']:
            count = severity_counts.get(severity, 0)
            percentage = (count / total_issues * 100) if total_issues > 0 else 0
            color = severity_colors.get(severity, 'white')
            
            severity_table.add_row(
                f"[{color}]{severity.upper()}[/{color}]",
                str(count),
                f"{percentage:.1f}%"
            )
        
        console.print(severity_table)
        
        
        # Group issues by category
        categorized_issues = {}
        for issue in result.issues:
            category = issue.category.value.replace('_', ' ').title()
            if category not in categorized_issues:
                categorized_issues[category] = []
            categorized_issues[category].append(issue)
            
        # Display issues by category
        for category, issues in categorized_issues.items():
            console.print(f"\n--- {category} ({len(issues)}) ---")
            max_display = min(20, len(issues))
            for i, issue in enumerate(issues[:max_display], 1):
                severity_color = severity_colors.get(issue.severity, 'white')
                
                issue_text = f"""
[{severity_color}]{issue.severity.upper()}[/{severity_color}] - {issue.title}
📁 {issue.file_path}:{issue.line_number or 'N/A'}
📝 {issue.description}
"""

                if show_insights:
                    if issue.ai_review_context:
                        issue_text += f"""
🤖 AI Review Context: {issue.ai_review_context}
"""
                    if issue.suggestion:
                        issue_text += f"""
🔧 Quick Fix:
{issue.suggestion}
"""
                    issue_text += f"""
⚠️  Impact: {issue.impact_score}/10
"""
                else:
                    if issue.suggestion:
                        issue_text += f"""
💡 {issue.suggestion}
"""
                
                console.print(Panel(issue_text, border_style=severity_color))
        
        # Show note if there are more issues
        if len(result.issues) > 20:
            remaining = len(result.issues) - 20
            console.print(f"\n📝 ... and {remaining} more issues (use --format json to see all)")
    
    return ""  # Rich console handles the output

def format_chat_response(response: ChatResponse) -> str:
    """Format chat response for CLI display"""
    
    # Main response
    console.print(Panel(response.message, title="🤖 Assistant", border_style="green"))
    
    # Suggestions
    if response.suggestions:
        console.print("\n💡 Follow-up suggestions:")
        for i, suggestion in enumerate(response.suggestions, 1):
            console.print(f"  {i}. {suggestion}")
    
    return ""  # Rich console handles the output

def get_detailed_resolution(issue) -> str:
    """Generate detailed resolution steps based on issue type"""
    
    resolution_guides = {
        # Security Issues
        "eval": """
1. 🚫 Remove eval() usage immediately
2. ✅ Use safer alternatives:
   • JSON.parse() for JSON data
   • Function constructor for dynamic functions
   • Template literals for string interpolation
3. 🔒 If dynamic code execution is needed:
   • Validate and sanitize all inputs
   • Use a sandboxed environment
   • Consider using a proper expression parser
4. 📚 Example fix:
   # Bad: eval(user_input)
   # Good: json.loads(user_input) or ast.literal_eval(user_input)
""",
        
        "shell injection": """
1. 🚫 Never use os.system() with user input
2. ✅ Use subprocess with proper escaping:
   • subprocess.run() with shell=False
   • Pass arguments as a list, not a string
3. 🔒 Input validation:
   • Whitelist allowed commands
   • Sanitize file paths
   • Use shlex.quote() for shell escaping
4. 📚 Example fix:
   # Bad: os.system(f"rm {user_file}")
   # Good: subprocess.run(["rm", user_file], check=True)
""",
        
        "innerHTML": """
1. 🚫 Avoid innerHTML with user data
2. ✅ Use safer alternatives:
   • textContent for plain text
   • createElement() + appendChild()
   • DOMPurify for HTML sanitization
3. 🔒 If HTML is needed:
   • Sanitize with a trusted library
   • Use Content Security Policy (CSP)
4. 📚 Example fix:
   # Bad: element.innerHTML = userInput
   # Good: element.textContent = userInput
""",
        
        # Performance Issues
        "nested loops": """
1. 🔍 Analyze algorithm complexity (currently O(n²))
2. ✅ Optimization strategies:
   • Use hash maps/dictionaries for lookups
   • Consider sorting + two-pointer technique
   • Break early when possible
   • Cache repeated calculations
3. 🚀 Alternative approaches:
   • Use built-in functions (filter, map, reduce)
   • Consider parallel processing for large datasets
4. 📚 Example fix:
   # Bad: nested for loops
   # Good: Use dictionary lookup or set operations
""",
        
        "dom query": """
1. 🚫 Avoid DOM queries inside loops
2. ✅ Cache DOM elements:
   • Query once, store in variable
   • Use document fragments for multiple elements
3. 🚀 Performance improvements:
   • Use event delegation
   • Batch DOM updates
   • Consider virtual DOM libraries
4. 📚 Example fix:
   # Bad: for(i=0;i<100;i++) document.getElementById('item'+i)
   # Good: const items = document.querySelectorAll('.item')
""",
        
        # Complexity Issues
        "high complexity": """
1. 🔍 Break down the function (current complexity > 10)
2. ✅ Refactoring strategies:
   • Extract smaller functions
   • Use early returns to reduce nesting
   • Replace nested if-else with switch/case
   • Use strategy pattern for complex logic
3. 🧹 Code organization:
   • Single Responsibility Principle
   • Use guard clauses
   • Consider state machines for complex flows
4. 📚 Example techniques:
   • Replace nested conditions with lookup tables
   • Use polymorphism instead of type checking
""",
        
        # Style Issues
        "var usage": """
1. 🚫 Replace 'var' with 'let' or 'const'
2. ✅ Modern JavaScript practices:
   • Use 'const' for values that don't change
   • Use 'let' for variables that need reassignment
   • Avoid 'var' due to function scoping issues
3. 🔒 Benefits:
   • Block scoping prevents bugs
   • Temporal dead zone catches errors
   • Better code readability
4. 📚 Example fix:
   # Bad: var name = "John"
   # Good: const name = "John" or let name = "John"
""",
        
        "console statement": """
1. 🚫 Remove console.log from production code
2. ✅ Better logging practices:
   • Use proper logging library (winston, pino)
   • Implement log levels (debug, info, warn, error)
   • Use environment-based logging
3. 🔧 Development alternatives:
   • Use debugger statements for debugging
   • Implement conditional logging
   • Use development/production builds
4. 📚 Example fix:
   # Bad: console.log("Debug info")
   # Good: logger.debug("Debug info") or remove entirely
"""
    }
    
    # Match issue to resolution guide
    issue_key = None
    issue_lower = issue.title.lower() + " " + issue.description.lower()
    
    if "eval" in issue_lower:
        issue_key = "eval"
    elif "shell" in issue_lower or "injection" in issue_lower:
        issue_key = "shell injection"
    elif "innerHTML" in issue_lower:
        issue_key = "innerHTML"
    elif "nested loop" in issue_lower or "loop" in issue_lower:
        issue_key = "nested loops"
    elif "dom query" in issue_lower or "getelementbyid" in issue_lower:
        issue_key = "dom query"
    elif "complexity" in issue_lower or "complex" in issue_lower:
        issue_key = "high complexity"
    elif "var" in issue_lower and "keyword" in issue_lower:
        issue_key = "var usage"
    elif "console" in issue_lower:
        issue_key = "console statement"
    
    if issue_key and issue_key in resolution_guides:
        return resolution_guides[issue_key]
    else:
        # Generic resolution steps
        return f"""
1. 🔍 Review the issue: {issue.description}
2. ✅ Apply the suggestion: {issue.suggestion}
3. 🧪 Test the fix thoroughly
4. 📚 Consider similar patterns in your codebase
5. 🔒 Follow security and performance best practices
6. 📖 Consult documentation for the specific technology/framework
"""

def get_concise_resolution(issue) -> str:
    """Generate concise resolution steps based on issue type"""
    
    concise_guides = {
        "eval": "🔧 Replace eval() with json.loads() or ast.literal_eval()\n📝 eval(user_input) → json.loads(user_input)\n⚠️  Prevents arbitrary code execution",
        
        "shell injection": "🔧 Use subprocess.run() with absolute paths and shell=False\n📝 os.system(cmd) → subprocess.run(['/usr/bin/tool', arg])\n⚠️  Prevents command injection",
        
        "innerHTML": "🔧 Use textContent instead of innerHTML for user data\n📝 element.innerHTML = data → element.textContent = data\n⚠️  Prevents XSS attacks",
        
        "nested loops": "🔧 Use hash maps or built-in functions to reduce complexity\n📝 for i in items: for j in items → use dictionary lookup\n⚠️  Improves performance from O(n²) to O(n)",
        
        "dom query": "🔧 Cache DOM elements outside loops\n📝 for(i=0;i<100;i++) getElementById() → cache elements first\n⚠️  Reduces DOM query overhead",
        
        "high complexity": "🔧 Break function into smaller functions with single responsibilities\n📝 Extract complex logic into separate methods\n⚠️  Improves maintainability and testing",
        
        "var usage": "🔧 Replace 'var' with 'const' or 'let'\n📝 var name = 'John' → const name = 'John'\n⚠️  Prevents scoping issues",
        
        "console statement": "🔧 Remove console.log() or use proper logging\n📝 console.log(msg) → logger.debug(msg) or remove\n⚠️  Keeps production code clean"
    }
    
    # Match issue to concise guide
    issue_lower = issue.title.lower() + " " + issue.description.lower()
    
    for key, guide in concise_guides.items():
        if key.replace(" ", "") in issue_lower.replace(" ", ""):
            return guide
    
    # Generic concise resolution
    return f"🔧 {issue.suggestion}\n⚠️  Impact: {issue.impact_score}/10"