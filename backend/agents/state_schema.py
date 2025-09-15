from typing import TypedDict, Annotated, List, Dict, Optional, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from backend.models.analysis_models import CodeIssue, FileMetrics, AnalysisResult

class CodeAnalysisState(TypedDict):
    # Input Parameters (from CLI)
    target_path: str
    include_patterns: List[str]
    severity_filter: Optional[str]
    insights_requested: bool
    model_choice: Literal['gemini', 'nebius']
    chat_mode: bool
    
    # File Discovery & Routing
    discovered_files: Dict[str, List[str]]  # language -> file_paths
    current_language: Optional[str]
    file_analysis_complete: Dict[str, bool]  # language -> completion_status
    
    # Analysis Results (Accumulated)
    all_issues: List[CodeIssue]
    python_issues: List[CodeIssue]
    javascript_issues: List[CodeIssue]
    file_metrics: List[FileMetrics]
    file_metadata: Dict[str, Dict]  # file_path -> metadata (truncated, description, etc.)
    
    # AI Agent Coordination
    analysis_strategy: Dict[str, any]  # AI-determined analysis approach
    current_batch: List[CodeIssue]     # For AI insights processing
    ai_insights_complete: bool
    
    # Chat & Context (Q&A Agent)
    conversation_history: Annotated[List[BaseMessage], add_messages]
    current_query: str
    analysis_context: Dict[str, any]   # Full analysis results for Q&A
    
    # Workflow Control
    current_step: str
    errors: List[str]
    analysis_complete: bool
    final_report: Optional[AnalysisResult]