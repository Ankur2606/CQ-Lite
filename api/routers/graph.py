"""
Dependency graph router
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models.api_models import GraphResponse, AnalysisJobStatus
from api.services.job_store import JobStore, get_job_store

router = APIRouter()

@router.get("/graph/{job_id}", response_model=GraphResponse)
async def get_dependency_graph(job_id: str, job_store: JobStore = Depends(get_job_store)):
    """
    Get the dependency graph for an analysis job
    """
    job = job_store.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    
    if job["status"] == AnalysisJobStatus.FAILED:
        error_message = job.get("error", "Unknown error during analysis")
        raise HTTPException(status_code=400, detail=f"Analysis failed: {error_message}")
    elif job["status"] != AnalysisJobStatus.COMPLETED:
        raise HTTPException(status_code=400, detail=f"Analysis is not complete. Current status: {job['status']}")
    
    # Check if dependency graph exists
    if "dependency_graph" not in job:
        raise HTTPException(status_code=404, detail="Dependency graph not found for this job")
    
    return GraphResponse(
        job_id=job_id,
        dependency_graph=job["dependency_graph"]
    )