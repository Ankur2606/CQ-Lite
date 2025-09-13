from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import os
import tempfile
import shutil
from pathlib import Path

from .analyzers.code_analyzer import CodeAnalyzer
from .services.gemini_service import GeminiService
from .models.analysis_models import AnalysisResult, ChatMessage, ChatResponse

app = FastAPI(
    title="Code Quality Intelligence Agent",
    description="AI-powered code analysis and quality insights",
    version="0.1.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
analyzer = CodeAnalyzer()
gemini_service = GeminiService()

class AnalyzeRequest(BaseModel):
    path: str
    include_patterns: Optional[List[str]] = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx"]

class ChatRequest(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None

@app.get("/")
async def root():
    return {"message": "Code Quality Intelligence Agent API"}

@app.post("/api/analyze", response_model=AnalysisResult)
async def analyze_code(request: AnalyzeRequest):
    """Analyze code at the specified path"""
    try:
        if not os.path.exists(request.path):
            raise HTTPException(status_code=404, detail="Path not found")
        
        result = await analyzer.analyze_path(request.path, request.include_patterns)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/upload")
async def upload_files(files: List[UploadFile] = File(...)):
    """Upload files for analysis"""
    try:
        # Create temporary directory
        temp_dir = tempfile.mkdtemp()
        uploaded_files = []
        
        for file in files:
            file_path = os.path.join(temp_dir, file.filename)
            with open(file_path, "wb") as buffer:
                shutil.copyfileobj(file.file, buffer)
            uploaded_files.append(file_path)
        
        # Analyze uploaded files
        result = await analyzer.analyze_path(temp_dir)
        
        # Cleanup
        shutil.rmtree(temp_dir)
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/chat", response_model=ChatResponse)
async def chat_about_code(request: ChatRequest):
    """Chat about the analyzed codebase"""
    try:
        response = await gemini_service.chat(request.message, request.context)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "services": {"analyzer": True, "gemini": True}}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)