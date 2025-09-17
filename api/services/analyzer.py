"""
Code analysis service that connects the FastAPI server with the existing analyzer tools
"""

from typing import List, Dict, Any, Optional
from fastapi import Depends
import sys
import os
import asyncio
from pathlib import Path

# Add the parent directory to the path for imports
sys.path.append(str(Path(__file__).parent.parent.parent))

from backend.agents.workflow import create_agentic_analysis_workflow
from backend.agents.state_schema import CodeAnalysisState
from backend.models.analysis_models import AnalysisResult, IssueSeverity
from api.models.api_models import ServiceType, AnalysisSummary, SeverityDistribution, SeverityCount

class AnalysisService:
    """Service for code analysis"""
    
    def __init__(self):
        """Initialize the analysis service"""
        self.workflow = create_agentic_analysis_workflow()
    
    async def analyze_path(
        self,
        path: str,
        include_patterns: List[str] = ["*.py", "*.js", "*.ts", "*.jsx", "*.tsx", "Dockerfile"],
        service: ServiceType = ServiceType.GEMINI
    ) -> AnalysisResult:
        """
        Analyze code at the given path using the agentic workflow
        
        Args:
            path: Path to the code to analyze
            include_patterns: File patterns to include
            service: AI service to use (gemini or nebius)
            
        Returns:
            Analysis results
        """
        print(f"Starting analysis on path: {path}")
        print(f"Using service: {service}")
        print(f"Include patterns: {include_patterns}")
        """
        Analyze code at the given path using the agentic workflow
        
        Args:
            path: Path to the code to analyze
            include_patterns: File patterns to include
            service: AI service to use (gemini or nebius)
            
        Returns:
            Analysis results
        """
        # Initialize the state for analysis
        initial_state = CodeAnalysisState(
            target_path=path,
            include_patterns=include_patterns,
            severity_filter=None,
            insights_requested=True,
            model_choice=service.value,
            skip_vector_store=False,
            chat_mode=False,
            discovered_files={},
            file_analysis_complete={},
            all_issues=[],
            python_issues=[],
            javascript_issues=[],
            file_metrics=[],
            analysis_strategy={},
            current_batch=[],
            ai_insights_complete=False,
            conversation_history=[],
            current_query="",
            analysis_context={},
            analysis_requested=False,
            detected_analysis_path=None,
            detected_model_choice=None,
            notion_reporting_enabled=False,
            current_step="start",
            errors=[],
            analysis_complete=False,
            final_report=None,
            github_files=[],
            is_github_repo=False
        )
        
        # Run the analysis workflow
        try:
            result = await self.workflow.ainvoke(initial_state)
            print(f"Analysis workflow completed successfully")
        except Exception as e:
            import traceback
            print(f"Error in analysis workflow: {str(e)}")
            print(traceback.format_exc())
            raise RuntimeError(f"Analysis workflow failed: {str(e)}")
        
        # Extract issues and create result
        issues = result.get("all_issues", [])
        
        # Calculate severity distribution
        severity_counts = {
            IssueSeverity.CRITICAL: 0,
            IssueSeverity.HIGH: 0,
            IssueSeverity.MEDIUM: 0,
            IssueSeverity.LOW: 0
        }
        
        for issue in issues:
            severity = issue.severity if hasattr(issue, "severity") else IssueSeverity.LOW
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        total_issues = sum(severity_counts.values())
        severity_distribution = {
            "CRITICAL": {"count": severity_counts[IssueSeverity.CRITICAL], 
                        "percentage": round(severity_counts[IssueSeverity.CRITICAL] / max(total_issues, 1) * 100, 1)},
            "HIGH": {"count": severity_counts[IssueSeverity.HIGH], 
                    "percentage": round(severity_counts[IssueSeverity.HIGH] / max(total_issues, 1) * 100, 1)},
            "MEDIUM": {"count": severity_counts[IssueSeverity.MEDIUM], 
                      "percentage": round(severity_counts[IssueSeverity.MEDIUM] / max(total_issues, 1) * 100, 1)},
            "LOW": {"count": severity_counts[IssueSeverity.LOW], 
                   "percentage": round(severity_counts[IssueSeverity.LOW] / max(total_issues, 1) * 100, 1)}
        }
        
        # Create a mock AnalysisResult for the API response
        total_files = sum(len(files) for files in result.get("discovered_files", {}).values())
        
        analysis_result = AnalysisResult(
            summary={
                "total_issues": total_issues,
                "severity_breakdown": severity_counts,
                "languages_detected": list(result.get("discovered_files", {}).keys()),
                "ai_review_summary": result.get("ai_review", {}).get("executive_summary", "")
            },
            issues=issues,
            metrics=result.get("file_metrics", []),
            total_files=total_files,
            total_lines=0,
            analysis_duration=0.0
        )
        
        return analysis_result


# Dependency injection for the analysis service
def get_analysis_service() -> AnalysisService:
    """Dependency for the analysis service"""
    return AnalysisService()