"""
FastAPI server for CQ Lite.
Provides API endpoints for GitHub repository analysis, file uploads, and dependency visualization.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, BackgroundTasks, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any, Union
import os
import uuid
import tempfile
import shutil
import json
import asyncio
from pathlib import Path
import sys

# Add the root directory to sys.path for imports
sys.path.append(str(Path(__file__).parent.parent))

from api.models.api_models import (
    GitHubAnalysisRequest, AnalysisResponse, AnalysisStatusResponse,
    ReportRequest, HealthResponse, GraphResponse
)
from api.routers import github, upload, report, status, graph
from api.services.analyzer import AnalysisService
from api.services.dependency_graph import DependencyGraphService

app = FastAPI(
    title="CQ Lite API",
    description="API for analyzing code quality and generating dependency graphs",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(github.router, prefix="/api", tags=["GitHub Analysis"])
app.include_router(upload.router, prefix="/api", tags=["File Upload"])
app.include_router(report.router, prefix="/api", tags=["Reports"])
app.include_router(status.router, prefix="/api", tags=["Analysis Status"])
app.include_router(graph.router, prefix="/api", tags=["Dependency Graph"])

@app.get("/")
async def root():
    """API root endpoint with basic information"""
    return {
        "name": "CQ Lite API",
        "version": "1.0.0",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    import datetime
    services_status = {
        "analyzer": True,
        "github_api": True,
        "gemini": os.environ.get("GOOGLE_API_KEY") is not None,
        "nebius": os.environ.get("NEBIUS_API_KEY") is not None,
        "notion": (os.environ.get("NOTION_TOKEN") is not None and 
                   os.environ.get("NOTION_PAGE_ID") is not None),
    }
    
    return {
        "status": "healthy",
        "services": services_status,
        "timestamp": str(datetime.datetime.now()),
    }

if __name__ == "__main__":
    import uvicorn
    import datetime
    uvicorn.run("api.main:app", host="0.0.0.0", port=8000, reload=True)

# Export the app for Vercel
handler = app