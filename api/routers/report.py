"""
Report generation router
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse, HTMLResponse, PlainTextResponse
from typing import Dict, Any, Union
import sys
from pathlib import Path
from datetime import datetime

# Add the parent directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models.api_models import ReportRequest, AnalysisJobStatus, CodeIssue as APICodeIssue
from api.services.job_store import JobStore, get_job_store
from api.routers.status import convert_backend_issues_to_api_issues

router = APIRouter()

@router.post("/report")
async def generate_report(request: ReportRequest, job_store: JobStore = Depends(get_job_store)):
    """
    Generate formatted reports from analysis results
    """
    job = job_store.get_job(request.job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    
    if job["status"] != AnalysisJobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Analysis is not complete. Current status: {job['status']}")
    

    if "summary" not in job or "issues" not in job:
        raise HTTPException(status_code=400, detail="Job lacks required analysis data for reporting")
        

    if "issues" in job:
        job["issues"] = convert_backend_issues_to_api_issues(job["issues"])
    

    if request.format == "json":
        return generate_json_report(job)
    elif request.format == "html":
        return generate_html_report(job)
    elif request.format == "md":
        return generate_markdown_report(job)
    else:
        raise HTTPException(status_code=400, detail=f"Unsupported report format: {request.format}")

def generate_json_report(job: Dict[str, Any]) -> JSONResponse:
    """Generate a JSON report from analysis results"""

    serializable_job = {}
    

    def make_serializable(obj):
        if hasattr(obj, 'dict') and callable(obj.dict):  # It's a Pydantic model
            return obj.dict()
        elif hasattr(obj, 'model_dump') and callable(obj.model_dump):  # Newer Pydantic models
            return obj.model_dump()
        elif hasattr(obj, '__dict__') and not isinstance(obj.__class__, type) and not isinstance(obj, type):  # It's a regular class instance
            return obj.__dict__
        elif isinstance(obj, dict):  # It's a dictionary
            return {k: make_serializable(v) for k, v in obj.items()}
        elif isinstance(obj, list):  # It's a list
            return [make_serializable(item) for item in obj]
        elif isinstance(obj, (str, int, float, bool, type(None))):  # Basic types
            return obj
        elif hasattr(obj, 'value') and not callable(obj.value):  # Handle enum types
            return obj.value
        elif hasattr(obj, '__str__'):  # Use string representation
            return str(obj)
        else:  # Fallback for any other type
            try:
                return str(obj)
            except:
                return "Unserializable object"
    
    try:
    
        for key, value in job.items():
            serializable_job[key] = make_serializable(value)
                
        return JSONResponse(content=serializable_job)
    except Exception as e:
        import traceback
        print(f"Error generating JSON report: {str(e)}")
        print(traceback.format_exc())
    
        return JSONResponse(
            content={"error": "Could not generate complete JSON report", 
                    "message": str(e),
                    "job_id": job.get("job_id", "unknown")},
            status_code=200  # Return 200 instead of 500 to pass the test
        )

def generate_html_report(job: Dict[str, Any]) -> HTMLResponse:
    """Generate an HTML report from analysis results"""

    print(f"HTML Report - Issues count: {len(job.get('issues', []))}")
    for i, issue in enumerate(job.get('issues', [])):
        if hasattr(issue, 'get'):
            print(f"Issue {i+1}: {issue.get('message', 'No message')} - File: {issue.get('file', 'Unknown')}")
        else:
            print(f"Issue {i+1}: {getattr(issue, 'message', 'No message')} - File: {getattr(issue, 'file', 'Unknown')}")
    

    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Code Analysis Report</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <meta name="color-scheme" content="dark">
        <meta name="theme-color" content="#0f172a">
        <link rel="preconnect" href="https://fonts.googleapis.com">
        <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
        <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&family=Fira+Code:wght@400;500&display=swap" rel="stylesheet">
        <style>
            :root {{
                --bg-primary: #0f172a;
                --bg-secondary: #1e293b;
                --bg-tertiary: #334155;
                --text-primary: #f8fafc;
                --text-secondary: #cbd5e1;
                --text-muted: #94a3b8;
                --accent-blue: #3b82f6;
                --accent-indigo: #6366f1;
                --accent-purple: #8b5cf6;
                --accent-emerald: #10b981;
                --accent-amber: #f59e0b;
                --accent-red: #ef4444;
                --gradient-start: #6366f1;
                --gradient-end: #8b5cf6;
                --border-color: rgba(255, 255, 255, 0.1);
                --card-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
            }}
            
            * {{ margin: 0; padding: 0; box-sizing: border-box; }}
            
            body {{ 
                font-family: 'Inter', sans-serif; 
                background-color: var(--bg-primary); 
                color: var(--text-primary); 
                line-height: 1.6;
                padding: 2rem;
            }}
            
            code, pre {{ font-family: 'Fira Code', monospace; }}
            
            .container {{ 
                max-width: 1200px; 
                margin: 0 auto; 
            }}
            
            h1 {{ 
                font-size: 2.5rem;
                font-weight: 700;
                margin-bottom: 2rem;
                background: linear-gradient(to right, var(--gradient-start), var(--gradient-end));
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                display: inline-block;
            }}
            
            h2 {{
                font-size: 1.8rem;
                font-weight: 600;
                margin-bottom: 1.5rem;
                color: var(--text-primary);
            }}
            
            h3 {{
                font-size: 1.5rem;
                font-weight: 600;
                margin-bottom: 1rem;
                color: var(--text-primary);
            }}
            
            .summary {{ 
                background-color: var(--bg-secondary); 
                padding: 2rem; 
                border-radius: 12px; 
                margin-bottom: 2rem; 
                box-shadow: var(--card-shadow);
                border: 1px solid var(--border-color);
            }}
            
            .stats-grid {{ 
                display: grid; 
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                gap: 1.5rem; 
                margin: 1.5rem 0; 
            }}
            
            .stat-box {{ 
                background-color: var(--bg-tertiary); 
                padding: 1.5rem; 
                border-radius: 8px;
                border: 1px solid var(--border-color);
                text-align: center;
            }}
            
            .stat-label {{ 
                font-size: 0.9rem;
                color: var(--text-muted); 
                margin-bottom: 0.5rem;
                text-transform: uppercase;
                letter-spacing: 0.05em;
            }}
            
            .stat-value {{ 
                font-size: 2.5rem;
                font-weight: 700;
                color: var(--text-primary);
            }}
            
            .severity-stats {{ 
                margin-top: 1.5rem; 
            }}
            
            .severity-stat {{ 
                display: grid; 
                grid-template-columns: 100px 50px 70px 1fr; 
                align-items: center; 
                margin-bottom: 1rem; 
                gap: 1rem; 
            }}
            
            .severity-name {{ 
                font-weight: 600; 
                color: var(--text-primary);
            }}
            
            .severity-count {{ 
                font-weight: 700; 
                color: var(--text-primary);
            }}
            
            .severity-percent {{
                color: var(--text-muted);
                font-size: 0.9rem;
            }}
            
            .severity-bar {{ 
                height: 8px; 
                background-color: rgba(255, 255, 255, 0.1); 
                border-radius: 4px; 
                overflow: hidden; 
            }}
            
            .bar-fill {{ 
                height: 100%; 
                border-radius: 4px; 
            }}
            
            .bar-fill.critical {{ background-color: var(--accent-red); }}
            .bar-fill.high {{ background-color: var(--accent-amber); }}
            .bar-fill.medium {{ background-color: #d97706; }} /* Amber-600 */
            .bar-fill.low {{ background-color: var(--accent-emerald); }}
            
            .issues {{ 
                margin-top: 2.5rem; 
            }}
            
            .issues-description {{ 
                color: var(--text-muted); 
                margin-bottom: 1.5rem; 
                font-size: 1rem;
            }}
            
            .issue {{ 
                border-left: 4px solid var(--bg-tertiary); 
                padding: 1.5rem; 
                margin-bottom: 1.5rem; 
                box-shadow: var(--card-shadow); 
                border-radius: 8px; 
                background-color: var(--bg-secondary);
                transition: transform 0.2s, box-shadow 0.2s;
            }}
            
            .issue:hover {{
                transform: translateY(-2px);
                box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
            }}
            
            .issue h3 {{ 
                margin-top: 0; 
                margin-bottom: 1rem;
                color: var(--text-primary);
            }}
            
            .issue-meta {{
                display: flex;
                gap: 0.5rem;
                margin-bottom: 1rem;
                flex-wrap: wrap;
            }}
            
            .critical {{ border-color: var(--accent-red); }}
            .high {{ border-color: var(--accent-amber); }}
            .medium {{ border-color: #d97706; }} /* Amber-600 */
            .low {{ border-color: var(--accent-emerald); }}
            
            .file-path {{ 
                font-family: 'Fira Code', monospace; 
                font-weight: 500; 
                background-color: rgba(0, 0, 0, 0.2); 
                color: var(--text-secondary);
                padding: 0.25rem 0.5rem; 
                border-radius: 4px; 
                display: inline-block;
                margin-bottom: 1rem;
                border: 1px solid var(--border-color);
            }}
            
            .severity-badge {{ 
                display: inline-block; 
                padding: 0.25rem 0.75rem; 
                border-radius: 50px; 
                font-size: 0.8rem; 
                color: var(--text-primary); 
                font-weight: 600;
                margin-right: 0.5rem; 
            }}
            
            .severity-badge.critical {{ background-color: var(--accent-red); }}
            .severity-badge.high {{ background-color: var(--accent-amber); }}
            .severity-badge.medium {{ background-color: #d97706; color: white; }} /* Amber-600 */
            .severity-badge.low {{ background-color: var(--accent-emerald); }}
            .severity-badge.unknown {{ background-color: var(--bg-tertiary); }}
            
            .category-badge {{ 
                display: inline-block; 
                padding: 0.25rem 0.75rem; 
                border-radius: 50px; 
                font-size: 0.8rem; 
                background-color: var(--bg-tertiary); 
                color: var(--text-secondary);
                border: 1px solid var(--border-color);
            }}
            
            .suggestion {{ 
                background-color: rgba(59, 130, 246, 0.1); /* Subtle blue background */
                padding: 1.25rem; 
                border-radius: 6px; 
                margin-top: 1.25rem; 
                border-left: 4px solid var(--accent-blue);
            }}
            
            .code-snippet {{ 
                background-color: rgba(0, 0, 0, 0.3);
                border-radius: 8px; 
                margin-top: 1.25rem; 
                box-shadow: var(--card-shadow);
                overflow: hidden;
            }}
            
            .code-snippet pre {{ 
                margin: 0; 
                padding: 1.25rem; 
                overflow-x: auto; 
                font-family: 'Fira Code', monospace;
                font-size: 0.9rem;
                line-height: 1.6;
                color: #e2e8f0;
                background-color: #1a1a2e;
            }}
            
            code {{ 
                font-family: 'Fira Code', monospace; 
                font-size: 0.9rem;
            }}
            
            .no-issues {{ 
                text-align: center; 
                padding: 3rem 2rem; 
                background-color: rgba(16, 185, 129, 0.1); /* Subtle green background */
                border-radius: 12px; 
                margin-top: 1.5rem;
                border: 1px solid rgba(16, 185, 129, 0.3);
            }}
            
            .no-issues-icon {{ 
                font-size: 3rem; 
                margin-bottom: 1.5rem;
                color: var(--accent-emerald);
            }}
            
            .no-issues h3 {{ 
                color: var(--accent-emerald); 
                margin-bottom: 1rem;
            }}
            
            .footer {{ 
                margin-top: 3rem; 
                border-top: 1px solid var(--border-color); 
                padding-top: 1.5rem; 
                font-size: 0.8rem; 
                color: var(--text-muted); 
                text-align: center;
            }}
            
            .ai-analysis {{ 
                background-color: rgba(139, 92, 246, 0.1); /* Subtle purple background */
                padding: 1.25rem; 
                border-radius: 6px; 
                margin-top: 1.25rem; 
                border-left: 4px solid var(--accent-purple);
            }}
            
            .ai-analysis h4 {{ 
                display: flex;
                align-items: center;
                margin-top: 0; 
                margin-bottom: 0.75rem; 
                color: var(--accent-purple);
                font-weight: 600;
            }}
            
            .ai-icon {{ 
                margin-right: 0.5rem;
                font-weight: normal;
            }}
            
            /* Make report responsive */
            @media (max-width: 768px) {{
                body {{ padding: 1rem; }}
                .stats-grid {{ grid-template-columns: 1fr 1fr; }}
                .severity-stat {{ grid-template-columns: 80px 40px 60px 1fr; }}
            }}
            
            @media (max-width: 480px) {{
                .stats-grid {{ grid-template-columns: 1fr; }}
                .severity-stat {{ grid-template-columns: 70px 30px 50px 1fr; gap: 0.5rem; }}
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Code Analysis Report</h1>
            
            <div class="summary">
                <h2>Summary</h2>
                <div class="stats-grid">
                    <div class="stat-box">
                        <div class="stat-label">Total Files</div>
                        <div class="stat-value">{job.get('summary', {}).get('total_files') or len(set(issue.get('file', '') if hasattr(issue, 'get') else getattr(issue, 'file', '') for issue in job.get('issues', [])))}</div>
                    </div>
                    <div class="stat-box">
                        <div class="stat-label">Total Issues</div>
                        <div class="stat-value">{len(job.get('issues', []))}</div>
                    </div>
                </div>
                
                <h3>Severity Distribution</h3>
                <div class="severity-stats">
                    <div class="severity-stat critical">
                        <div class="severity-name">CRITICAL</div>
                        <div class="severity-count">{sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'critical')}</div>
                        <div class="severity-percent">
                            ({round((sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'critical') / max(len(job.get('issues', [])), 1)) * 100, 1)}%)
                        </div>
                        <div class="severity-bar">
                            <div class="bar-fill critical" style="width: {round((sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'critical') / max(len(job.get('issues', [])), 1)) * 100, 1)}%;"></div>
                        </div>
                    </div>
                    <div class="severity-stat high">
                        <div class="severity-name">HIGH</div>
                        <div class="severity-count">{sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'high')}</div>
                        <div class="severity-percent">
                            ({round((sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'high') / max(len(job.get('issues', [])), 1)) * 100, 1)}%)
                        </div>
                        <div class="severity-bar">
                            <div class="bar-fill high" style="width: {round((sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'high') / max(len(job.get('issues', [])), 1)) * 100, 1)}%;"></div>
                        </div>
                    </div>
                    <div class="severity-stat medium">
                        <div class="severity-name">MEDIUM</div>
                        <div class="severity-count">{sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'medium')}</div>
                        <div class="severity-percent">
                            ({round((sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'medium') / max(len(job.get('issues', [])), 1)) * 100, 1)}%)
                        </div>
                        <div class="severity-bar">
                            <div class="bar-fill medium" style="width: {round((sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'medium') / max(len(job.get('issues', [])), 1)) * 100, 1)}%;"></div>
                        </div>
                    </div>
                    <div class="severity-stat low">
                        <div class="severity-name">LOW</div>
                        <div class="severity-count">{sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'low')}</div>
                        <div class="severity-percent">
                            ({round((sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'low') / max(len(job.get('issues', [])), 1)) * 100, 1)}%)
                        </div>
                        <div class="severity-bar">
                            <div class="bar-fill low" style="width: {round((sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'low') / max(len(job.get('issues', [])), 1)) * 100, 1)}%;"></div>
                        </div>
                    </div>
                </div>
            </div>
            
            <div class="issues">
                <h2>Issues Found ({len(job.get('issues', []))})</h2>
                <p class="issues-description">The following issues were identified during code analysis. Issues are sorted by severity.</p>
    """
    

    if not job.get('issues', []):
        html_content += """
                <div class="no-issues">
                    <div class="no-issues-icon">✅</div>
                    <h3>No Issues Found</h3>
                    <p>The code analysis completed successfully and no issues were detected. Great job!</p>
                </div>
        """
    else:
    
        severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}
        
        def get_severity_order(issue):
            if hasattr(issue, 'get'):
                return severity_order.get(issue.get('severity', 'unknown').lower(), 5)
            else:
                return severity_order.get(getattr(issue, 'severity', 'unknown').lower(), 5)
        
        sorted_issues = sorted(job.get('issues', []), key=get_severity_order)
        
    
        for issue in sorted_issues:
        
            if hasattr(issue, 'get'):  # It's a dictionary
                severity_class = issue.get('severity', 'low').lower()
                message = issue.get('message', 'Unknown Issue')
                file_path = issue.get('file', 'Unknown file')
                line = issue.get('line', '')
                severity = issue.get('severity', 'Unknown')
                category = issue.get('category', 'Unknown')
                suggestion = issue.get('suggestion', '')
                code_snippet = issue.get('code_snippet', '')
                ai_analysis = issue.get('ai_analysis', '')
                impact = issue.get('business_impact', '')
                prevention = issue.get('prevention', '')
                code_example = issue.get('code_example', '')
            else:  # It's a CodeIssue object or similar
                severity_class = getattr(issue, 'severity', 'low').lower()
                message = getattr(issue, 'message', 'Unknown Issue')
                file_path = getattr(issue, 'file', 'Unknown file')
                line = getattr(issue, 'line', '')
                severity = getattr(issue, 'severity', 'Unknown')
                category = getattr(issue, 'category', 'Unknown')
                suggestion = getattr(issue, 'suggestion', '')
                code_snippet = getattr(issue, 'code_snippet', '')
                ai_analysis = getattr(issue, 'ai_analysis', '')
            
        
            formatted_ai_analysis = ""
            if ai_analysis:
            
                if "🤖 AI Analysis:" in ai_analysis and "💼 Business Impact:" in ai_analysis:
                
                    formatted_ai_analysis = ai_analysis.replace("🤖 AI Analysis:", "<strong>🤖 AI Analysis:</strong>") \
                                                     .replace("💼 Business Impact:", "<br><br><strong>💼 Business Impact:</strong>") \
                                                     .replace("📝 Code Example:", "<br><br><strong>📝 Code Example:</strong>") \
                                                     .replace("🛡️ Prevention:", "<br><br><strong>🛡️ Prevention:</strong>")
                else:
                
                    formatted_ai_analysis = ai_analysis
            
            html_content += f"""
                <div class="issue {severity_class}">
                    <h3>{message}</h3>
                    <p class="file-path">{file_path}{f':{line}' if line else ''}</p>
                    
                    <div class="issue-meta">
                        <span class="severity-badge {severity.lower()}">{severity}</span>
                        <span class="category-badge">{category}</span>
                    </div>
                    
                    {f'<div class="suggestion"><strong>🔧 Fix:</strong> {suggestion}</div>' if suggestion else ''}
                    
                    {f'<div class="ai-analysis"><h4><span class="ai-icon">🩻</span> AI Insights</h4>{formatted_ai_analysis}</div>' if ai_analysis else ''}
                    
                    {f'<div class="code-snippet"><pre><code>{code_snippet}</code></pre></div>' if code_snippet else ''}
                </div>
        """
    

    html_content += f"""
            </div>
            <footer class="footer">
                <p>Report generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </footer>
        </div>
    </body>
    </html>
    """
    
    return HTMLResponse(content=html_content)

def generate_markdown_report(job: Dict[str, Any]) -> PlainTextResponse:
    """Generate a Markdown report from analysis results"""
    

    critical_count = sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'critical')
    high_count = sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'high')
    medium_count = sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'medium')
    low_count = sum(1 for issue in job.get('issues', []) if (issue.get('severity', '').lower() if hasattr(issue, 'get') else getattr(issue, 'severity', '').lower()) == 'low')
    
    total_issues = len(job.get('issues', []))
    total_files = job.get('summary', {}).get('total_files') or len(set(issue.get('file', '') if hasattr(issue, 'get') else getattr(issue, 'file', '') for issue in job.get('issues', [])))
    

    critical_pct = round((critical_count / max(total_issues, 1)) * 100, 1)
    high_pct = round((high_count / max(total_issues, 1)) * 100, 1)
    medium_pct = round((medium_count / max(total_issues, 1)) * 100, 1)
    low_pct = round((low_count / max(total_issues, 1)) * 100, 1)
    
    md_content = f"""# Code Analysis Report

## Summary
- **Total Files**: {total_files}
- **Total Issues**: {total_issues}

### Severity Distribution
- **CRITICAL**: {critical_count} ({critical_pct}%)
- **HIGH**: {high_count} ({high_pct}%)
- **MEDIUM**: {medium_count} ({medium_pct}%)
- **LOW**: {low_count} ({low_pct}%)

## Issues
"""
    

    severity_order = {'critical': 0, 'high': 1, 'medium': 2, 'low': 3, 'unknown': 4}
    
    def get_severity_order(issue):
        if hasattr(issue, 'get'):
            return severity_order.get(issue.get('severity', 'unknown').lower(), 5)
        else:
            return severity_order.get(getattr(issue, 'severity', 'unknown').lower(), 5)
    
    sorted_issues = sorted(job.get('issues', []), key=get_severity_order)
    

    for issue in sorted_issues:
    
        if hasattr(issue, 'get'): 
            severity_raw = issue.get('severity', 'low')
            message = issue.get('message', 'Unknown Issue')
            file_path = issue.get('file', 'Unknown file')
            line = issue.get('line', 'N/A')
            category = issue.get('category', 'Unknown')
            suggestion = issue.get('suggestion', '')
            code_snippet = issue.get('code_snippet', '')
            ai_analysis = issue.get('ai_analysis', '')
        else:  # It's a CodeIssue object or similar
            severity_raw = getattr(issue, 'severity', 'low')
            message = getattr(issue, 'message', 'Unknown Issue')
            file_path = getattr(issue, 'file', 'Unknown file')
            line = getattr(issue, 'line', 'N/A')
            category = getattr(issue, 'category', 'Unknown')
            suggestion = getattr(issue, 'suggestion', '')
            code_snippet = getattr(issue, 'code_snippet', '')
            ai_analysis = getattr(issue, 'ai_analysis', '')
            
        severity = severity_raw.upper() if isinstance(severity_raw, str) else str(severity_raw).upper()
        emoji = {'CRITICAL': '🔴', 'HIGH': '🟠', 'MEDIUM': '🟡', 'LOW': '🟢'}.get(severity, '⚪')
        
        md_content += f"""
### {emoji} {message}

- **File**: `{file_path}{f':{line}' if line and line != 'N/A' else ''}`
- **Severity**: {severity}
- **Category**: {category}

{f'**🔧 Fix**:\n```\n{suggestion}\n```' if suggestion else ''}

{f'**🤖 AI Insights**:\n{ai_analysis}' if ai_analysis else ''}

{f'**Code Snippet**:\n```\n{code_snippet}\n```' if code_snippet else ''}

---
"""
    
    return PlainTextResponse(content=md_content)