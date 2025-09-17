"""
GitHub repository analysis router
"""

import datetime  
from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional
import uuid
import asyncio
import os
import sys
from pathlib import Path


sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models.api_models import GitHubAnalysisRequest, AnalysisResponse, AnalysisJobStatus
from api.services.analyzer import AnalysisService, get_analysis_service
from api.services.dependency_graph import DependencyGraphService, get_graph_service
from api.services.job_store import JobStore, get_job_store
from backend.tools.github_tool import fetch_repo_files, parse_github_url, GitHubAPIException

router = APIRouter()

@router.post("/analyze/github", response_model=AnalysisResponse)
async def analyze_github_repo(
    request: GitHubAnalysisRequest,
    background_tasks: BackgroundTasks,
    analysis_service: AnalysisService = Depends(get_analysis_service),
    graph_service: DependencyGraphService = Depends(get_graph_service),
    job_store: JobStore = Depends(get_job_store)
):
    """
    Analyze a GitHub repository for code quality issues and generate dependency graphs
    """
    
    job_id = str(uuid.uuid4())
    

    job_store.add_job(job_id, {
        "job_id": job_id,
        "status": AnalysisJobStatus.PENDING,
        "repo_url": request.repo_url,
        "service": request.service,
        "include_notion": request.include_notion,
        "created_at": str(datetime.datetime.now()),
    })
    
    # Add task to background
    background_tasks.add_task(
        process_github_analysis,
        job_id,
        request,
        analysis_service,
        graph_service,
        job_store
    )
    
    # Return initial response
    return AnalysisResponse(
        job_id=job_id,
        status=AnalysisJobStatus.PENDING,
        created_at=datetime.datetime.now()
    )

async def process_github_analysis(
    job_id: str, 
    request: GitHubAnalysisRequest, 
    analysis_service: AnalysisService,
    graph_service: DependencyGraphService,
    job_store: JobStore
):
    """Process GitHub repository analysis in the background"""
    try:
        # Update job status
        job_store.update_job(job_id, {"status": AnalysisJobStatus.PROCESSING})
        
        # Parse GitHub URL
        repo_info = parse_github_url(request.repo_url)
        owner = repo_info["owner"]
        repo = repo_info["repo"]
        
        # Fetch repository files using your existing tools
        github_token = os.environ.get("GITHUB_API_TOKEN")
        print(f"Fetching GitHub repository: {request.repo_url}")
        print(f"Repository: {owner}/{repo}")
        github_files = fetch_repo_files(
            request.repo_url,
            token=github_token,
            max_files=request.max_files
        )
        
        if not github_files:
            raise ValueError("No files fetched from the repository")
        
        # Create a temporary directory to store the fetched files
        temp_dir = f"temp-github-{owner}-{repo}"
        os.makedirs(temp_dir, exist_ok=True)
        
        # Save the files to the temp directory
        for github_file in github_files:
            file_path = os.path.join(temp_dir, github_file["file_path"])
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(github_file["content"])
        
        # Run analysis on the temporary directory
        analysis_result = await analysis_service.analyze_path(
            temp_dir, 
            include_patterns=request.include_patterns,
            service=request.service
        )
        
        # Generate dependency graph
        dependency_graph = await graph_service.generate_graph(temp_dir)
        
        # Let the analysis results flow naturally
        # If there's an issue, it will be caught in the main exception handler
        
        # Debug the issues before storing them
        print("\n------ DEBUG: GitHub Analysis Issues ------")
        for idx, issue in enumerate(analysis_result.issues):
            print(f"Issue {idx} type: {type(issue)}")
            if hasattr(issue, "__dict__"):
                print(f"  Attributes: {issue.__dict__}")
            print(f"  File: {getattr(issue, 'file_path', None)}")
            print(f"  Line: {getattr(issue, 'line_number', None)}")
            print(f"  Title: {getattr(issue, 'title', None)}")
        
        # Update job with results
        job_store.update_job(job_id, {
            "status": AnalysisJobStatus.COMPLETED,
            "summary": analysis_result.summary,
            "issues": analysis_result.issues,
            "dependency_graph": dependency_graph,
            "completed_at": str(datetime.datetime.now())
        })
        
    except GitHubAPIException as e:
        # Properly mark the job as failed with the actual error
        error_msg = f"GitHub API error: {str(e)}"
        print(f"GitHub analysis failed: {error_msg}")
        job_store.update_job(job_id, {
            "status": AnalysisJobStatus.FAILED,
            "error": error_msg,
            "completed_at": str(datetime.datetime.now())
        })
    except Exception as e:
        # Handle any other exceptions properly
        import traceback
        error_msg = f"Analysis failed: {str(e)}"
        print(f"GitHub analysis error: {error_msg}")
        print(traceback.format_exc())
        job_store.update_job(job_id, {
            "status": AnalysisJobStatus.FAILED, 
            "error": error_msg,
            "completed_at": str(datetime.datetime.now())
        })
