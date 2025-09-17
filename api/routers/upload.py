"""
File upload analysis router
"""

from fastapi import APIRouter, HTTPException, BackgroundTasks, Depends, UploadFile, File
from fastapi.responses import JSONResponse
from typing import List, Dict, Any
import uuid
import os
import shutil
import tempfile
import datetime
import sys
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from api.models.api_models import UploadAnalysisRequest, AnalysisResponse, AnalysisJobStatus
from api.services.analyzer import AnalysisService, get_analysis_service
from api.services.dependency_graph import DependencyGraphService, get_graph_service
from api.services.job_store import JobStore, get_job_store

router = APIRouter()

@router.post("/analyze/upload", response_model=AnalysisResponse)
async def analyze_uploaded_files(
    files: List[UploadFile] = File(...),
    request: UploadAnalysisRequest = Depends(),
    background_tasks: BackgroundTasks = BackgroundTasks(),
    analysis_service: AnalysisService = Depends(get_analysis_service),
    graph_service: DependencyGraphService = Depends(get_graph_service),
    job_store: JobStore = Depends(get_job_store)
):
    """
    Analyze uploaded files for code quality issues and generate dependency graphs
    """
    if not files:
        raise HTTPException(status_code=400, detail="No files uploaded")
    
    # Check file limit based on the requested max_files
    if len(files) > request.max_files:
        raise HTTPException(status_code=400, detail=f"Maximum {request.max_files} files allowed for upload")
    
    # Generate a job ID
    job_id = str(uuid.uuid4())
    
    # Create initial job status
    job_store.add_job(job_id, {
        "job_id": job_id,
        "status": AnalysisJobStatus.PENDING,
        "service": request.service,
        "include_notion": request.include_notion,
        "created_at": str(datetime.datetime.now()),
    })
    
    # Read all file contents first before passing to background task
    file_contents = []
    for file in files:
        try:
            # Read file content
            contents = await file.read()
            file_contents.append({
                "filename": file.filename,
                "content": contents
            })
            # Reset file pointer for potential future use
            await file.seek(0)
        except Exception as e:
            print(f"Error reading file {file.filename}: {str(e)}")
            raise HTTPException(status_code=500, detail=f"Error reading file {file.filename}: {str(e)}")
    
    # Add task to background
    background_tasks.add_task(
        process_uploaded_files,
        job_id,
        file_contents,  # Pass file contents instead of file objects
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

async def process_uploaded_files(
    job_id: str,
    file_contents: List[Dict[str, Any]],  # List of dicts with filename and content
    request: UploadAnalysisRequest,
    analysis_service: AnalysisService,
    graph_service: DependencyGraphService,
    job_store: JobStore
):
    """Process uploaded files in the background"""
    temp_dir = None
    try:
        # Update job status
        job_store.update_job(job_id, {"status": AnalysisJobStatus.PROCESSING})
        
        # Create a temporary directory for the uploaded files
        temp_dir = tempfile.mkdtemp(prefix="upload-analysis-")
        print(f"Created temporary directory: {temp_dir}")
        
        # Save uploaded files to the temporary directory
        for file_data in file_contents:
            filename = file_data["filename"]
            content = file_data["content"]
            
            file_path = os.path.join(temp_dir, filename)
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            
            # Save the file content
            with open(file_path, "wb") as f:
                f.write(content)
                
            print(f"Saved file {filename} to {file_path}")
        
        # Run analysis on the temporary directory
        analysis_result = await analysis_service.analyze_path(
            temp_dir,
            service=request.service
        )
        
        # Generate dependency graph - let errors be caught naturally
        dependency_graph = await graph_service.generate_graph(temp_dir)
            
        # No need for mock data - the actual analysis service should provide results
        # If there's an error, it will be caught in the exception handler
        
        # Update job with results
        job_store.update_job(job_id, {
            "status": AnalysisJobStatus.COMPLETED,
            "summary": analysis_result.summary,
            "issues": analysis_result.issues,
            "dependency_graph": dependency_graph,
            "completed_at": str(datetime.datetime.now())
        })
        
    except Exception as e:
        # Add better error details for debugging
        import traceback
        error_msg = f"Upload analysis failed: {str(e)}"
        print(error_msg)
        print(traceback.format_exc())
        job_store.update_job(job_id, {
            "status": AnalysisJobStatus.FAILED,
            "error": error_msg,
            "completed_at": str(datetime.datetime.now())
        })
    finally:
        # Clean up temporary directory
        if temp_dir and os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)