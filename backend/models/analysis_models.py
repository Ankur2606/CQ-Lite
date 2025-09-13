from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from enum import Enum

class IssueSeverity(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class IssueCategory(str, Enum):
    SECURITY = "security"
    PERFORMANCE = "performance"
    DUPLICATION = "duplication"
    COMPLEXITY = "complexity"
    TESTING = "testing"
    DOCUMENTATION = "documentation"
    STYLE = "style"

class CodeIssue(BaseModel):
    id: str
    category: IssueCategory
    severity: IssueSeverity
    title: str
    description: str
    file_path: str
    line_number: Optional[int] = None
    column_number: Optional[int] = None
    code_snippet: Optional[str] = None
    suggestion: str
    impact_score: float  # 0-10 scale

class FileMetrics(BaseModel):
    file_path: str
    language: str
    lines_of_code: int
    complexity_score: float
    duplication_percentage: float
    test_coverage: Optional[float] = None

class AnalysisResult(BaseModel):
    summary: Dict[str, Any]
    issues: List[CodeIssue]
    metrics: List[FileMetrics]
    total_files: int
    total_lines: int
    analysis_duration: float

class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None

class ChatResponse(BaseModel):
    message: str
    context_used: bool
    suggestions: Optional[List[str]] = None