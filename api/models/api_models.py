"""
Pydantic models for API requests and responses
"""

from pydantic import BaseModel, Field, HttpUrl
from typing import List, Dict, Any, Optional, Union
from enum import Enum
import datetime
import uuid


class AnalysisJobStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


class ServiceType(str, Enum):
    GEMINI = "gemini"
    NEBIUS = "nebius"


class GitHubAnalysisRequest(BaseModel):
    """Request model for GitHub repository analysis"""
    repo_url: str = Field(..., description="GitHub repository URL to analyze")
    service: ServiceType = Field(default=ServiceType.GEMINI, description="AI service to use")
    include_notion: bool = Field(default=False, description="Whether to push results to Notion")
    max_files: int = Field(default=100, description="Maximum number of files to analyze")
    include_patterns: List[str] = Field(
        default=["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "Dockerfile"],
        description="File patterns to include in analysis"
    )


class UploadAnalysisRequest(BaseModel):
    """Request model for uploaded files analysis"""
    service: ServiceType = Field(default=ServiceType.GEMINI, description="AI service to use")
    include_notion: bool = Field(default=False, description="Whether to push results to Notion")
    max_files: int = Field(default=12, description="Maximum number of files to analyze")


class ReportRequest(BaseModel):
    """Request model for generating formatted reports"""
    job_id: str = Field(..., description="ID of the analysis job")
    format: str = Field(default="html", description="Report format (html, md, json)")


class SeverityCount(BaseModel):
    """Model for severity count statistics"""
    count: int
    percentage: float


class SeverityDistribution(BaseModel):
    """Model for severity distribution"""
    CRITICAL: SeverityCount
    HIGH: SeverityCount
    MEDIUM: SeverityCount
    LOW: SeverityCount


class AnalysisSummary(BaseModel):
    """Summary of analysis results"""
    total_files: int
    total_issues: int
    severity_distribution: SeverityDistribution


class GraphNode(BaseModel):
    """Node in the dependency graph"""
    id: str
    name: Optional[str] = None  # Display name for the node (usually filename)
    group: int
    type: str
    size: int


class GraphLink(BaseModel):
    """Link in the dependency graph"""
    source: str
    target: str
    value: int


class DependencyGraph(BaseModel):
    """Dependency graph structure"""
    nodes: List[GraphNode]
    links: List[GraphLink]


class CodeIssue(BaseModel):
    """Model for code issues detected"""
    file: str
    line: Optional[int] = None
    severity: str
    category: str
    message: str
    suggestion: Optional[str] = None
    code_snippet: Optional[str] = None
    
    def __init__(self, **data):
        print(f"DEBUG: Creating API CodeIssue with line={data.get('line')}, file={data.get('file')}")
        super().__init__(**data)


class AnalysisResponse(BaseModel):
    """Response model for analysis results"""
    job_id: str
    status: AnalysisJobStatus
    summary: Optional[AnalysisSummary] = None
    dependency_graph: Optional[DependencyGraph] = None
    issues: Optional[List[CodeIssue]] = None
    created_at: datetime.datetime = Field(default_factory=datetime.datetime.now)
    completed_at: Optional[datetime.datetime] = None


class AnalysisStatusResponse(BaseModel):
    """Response model for analysis job status"""
    job_id: str
    status: AnalysisJobStatus
    progress: Optional[float] = None
    message: Optional[str] = None
    error: Optional[str] = None
    created_at: datetime.datetime
    updated_at: datetime.datetime = Field(default_factory=datetime.datetime.now)


class GraphResponse(BaseModel):
    """Response model for dependency graph"""
    job_id: str
    dependency_graph: DependencyGraph


class HealthResponse(BaseModel):
    """Response model for health check"""
    status: str
    services: Dict[str, bool]
    timestamp: str


class WebSocketMessage(BaseModel):
    """WebSocket message model for real-time updates"""
    job_id: str
    type: str
    data: Dict[str, Any]