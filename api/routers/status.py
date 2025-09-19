"""
Status checking router for analysis jobs
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any, List
import datetime
import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models.api_models import AnalysisStatusResponse, AnalysisJobStatus, CodeIssue as APICodeIssue
from api.services.job_store import get_job_store, JobStore
from backend.models.analysis_models import CodeIssue as BackendCodeIssue

router = APIRouter()

def convert_backend_issues_to_api_issues(backend_issues: List[Any]) -> List[APICodeIssue]:
    """
    Convert backend.models.analysis_models.CodeIssue to api.models.api_models.CodeIssue objects
    
    This handles the differences between the backend and API models for CodeIssue objects
    """
    print(f"\n------ DEBUG: Converting {len(backend_issues)} issues ------")
    for idx, issue in enumerate(backend_issues):
        print(f"Original issue {idx}: {type(issue)}")
    
        if hasattr(issue, "__dict__"):
            print(f"  Attributes: {issue.__dict__}")
        elif isinstance(issue, dict):
            print(f"  Dict keys: {issue.keys()}")
            print(f"  Line number/file info: {issue.get('line_number')}, {issue.get('file_path')}")
    
    api_issues = []
    
    for issue in backend_issues:
        try:
        
            if hasattr(issue, 'file') and hasattr(issue, 'message'):
                api_issues.append(issue)
                print(f"Already API model: {issue}")
                continue
                
        
            if hasattr(issue, 'file_path') or hasattr(issue, 'title') or hasattr(issue, 'description'):
            
                if hasattr(issue, 'model_dump'):
                
                    issue_dict = issue.model_dump()
                elif hasattr(issue, 'dict'):
                
                    issue_dict = issue.dict()
                elif hasattr(issue, '__dict__'):
                
                    issue_dict = issue.__dict__
                else:
                
                    issue_dict = issue
                    
            
            
                severity = issue_dict.get('severity', "low")
                if hasattr(severity, 'value'):
                    severity = severity.value
                
                category = issue_dict.get('category', "unknown")
                if hasattr(category, 'value'):
                    category = category.value
                
            
                print(f"  Mapping backend to API model:")
                print(f"    file_path: {issue_dict.get('file_path')}")
                print(f"    line_number: {issue_dict.get('line_number')}")
                print(f"    title: {issue_dict.get('title')}")
                print(f"    description: {issue_dict.get('description')}")
                
                api_issue = APICodeIssue(
                    file=issue_dict.get('file_path', "Unknown file"),
                    line=issue_dict.get('line_number'),
                    severity=severity,
                    category=category,
                    message=issue_dict.get('title', issue_dict.get('description', "No message")),
                    suggestion=issue_dict.get('suggestion', None),
                    code_snippet=issue_dict.get('code_snippet', None),
                    ai_analysis=issue_dict.get('ai_review_context', None)
                )
                api_issues.append(api_issue)
                print(f"  Created API issue: file={api_issue.file}, line={api_issue.line}")
            else:
            
                api_issues.append(APICodeIssue(
                    file=issue.get('file', "Unknown file"),
                    line=issue.get('line'),
                    severity=issue.get('severity', "low"),
                    category=issue.get('category', "unknown"),
                    message=issue.get('message', "No message"),
                    suggestion=issue.get('suggestion'),
                    code_snippet=issue.get('code_snippet'),
                    ai_analysis=issue.get('ai_analysis')
                ))
                
        except Exception as e:
        
            print(f"Error converting issue: {str(e)}")
            api_issues.append(APICodeIssue(
                file="Unknown file",
                severity="low",
                category="unknown",
                message=f"Issue conversion error: {str(e)}"
            ))
            

    print("\n------ DEBUG: Converted API issues ------")
    for idx, issue in enumerate(api_issues):
        print(f"API issue {idx}: file={issue.file}, line={issue.line}, message={issue.message}, severity={issue.severity}")
    
    return api_issues

@router.get("/status/{job_id}")
async def get_analysis_status(
    job_id: str, 
    include_details: bool = False,
    job_store: JobStore = Depends(get_job_store)
):
    """
    Get the status of an analysis job.
    
    Parameters:
    - job_id: ID of the job to retrieve
    - include_details: If True, returns the full job details including analysis results
    """
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    

    created_at = datetime.datetime.fromisoformat(job["created_at"]) if isinstance(job["created_at"], str) else job["created_at"]
    

    status_response = AnalysisStatusResponse(
        job_id=job_id,
        status=job["status"],
        progress=job.get("progress", None),
        message=job.get("message", None),
        error=job.get("error", None) if job["status"] == AnalysisJobStatus.FAILED else None,
        created_at=created_at,
        updated_at=datetime.datetime.now()
    )
    

    if include_details:
    
        response_data = status_response.dict()
        
    
        if job.get("summary"):
            response_data["summary"] = job["summary"]
        if job.get("issues"):
        
            response_data["issues"] = convert_backend_issues_to_api_issues(job["issues"])
        if job.get("error"):
            response_data["error"] = job["error"]
        
        return response_data
    
    return status_response