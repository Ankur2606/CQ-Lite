from typing import TypedDict, Annotated, List, Dict, Optional, Literal
from langgraph.graph.message import add_messages
from langchain_core.messages import BaseMessage
from backend.models.analysis_models import CodeIssue, FileMetrics, AnalysisResult

class CodeAnalysisState(TypedDict):

    target_path: str
    include_patterns: List[str]
    severity_filter: Optional[str]
    insights_requested: bool
    model_choice: Literal['gemini', 'nebius']
    skip_vector_store: bool
    chat_mode: bool
    max_files_limit: Optional[int]  # Maximum number of files to analyze
    

    github_files: List[Dict]  # List of files from GitHub API
    is_github_repo: bool  
    

    discovered_files: Dict[str, List[str]]  # language -> file_paths
    current_language: Optional[str]
    file_analysis_complete: Dict[str, bool]  # language -> completion_status
    

    all_issues: List[CodeIssue]
    python_issues: List[CodeIssue]
    javascript_issues: List[CodeIssue]
    docker_issues: List[CodeIssue]
    file_metrics: List[FileMetrics]
    file_metadata: Dict[str, Dict]  # file_path -> metadata (truncated, description, etc.)
    

    analysis_strategy: Dict[str, any]  # AI-determined analysis approach
    current_batch: List[CodeIssue] 
    ai_insights_complete: bool
    

    conversation_history: Annotated[List[BaseMessage], add_messages]
    current_query: str
    analysis_context: Dict[str, any]   # Full analysis results for Q&A
    

    chat_mode: bool
    analysis_requested: bool
    detected_analysis_path: Optional[str]
    detected_model_choice: Optional[str]
    

    notion_reporting_enabled: bool
    

    current_step: str
    errors: List[str]
    analysis_complete: bool
    final_report: Optional[AnalysisResult]