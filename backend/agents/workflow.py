from langgraph.graph import StateGraph, START, END
from .state_schema import CodeAnalysisState
from .file_discovery_agent import file_discovery_agent
from .python_analysis_agent import python_analysis_agent
from .ai_review_agent import ai_review_agent

def route_language_analysis(state: CodeAnalysisState) -> str:
    """AI-driven routing based on analysis strategy"""
    strategy = state.get("analysis_strategy", {})
    discovered = state.get("discovered_files", {})
    
    has_python = len(discovered.get("python", [])) > 0
    has_js = len(discovered.get("javascript", [])) > 0
    
    if not has_python and not has_js:
        return "no_files"
    
    # Use AI strategy to determine routing
    if strategy.get("parallel_processing", False) and has_python and has_js:
        return "python_analysis"  # Start with Python, JS will follow
    elif strategy.get("python_priority", True) and has_python:
        return "python_analysis"
    elif has_js:
        return "javascript_analysis"
    else:
        return "no_files"

def check_analysis_completion(state: CodeAnalysisState) -> str:
    """Check if all required analysis is complete"""
    completion_status = state.get("file_analysis_complete", {})
    discovered = state.get("discovered_files", {})
    
    python_needed = len(discovered.get("python", [])) > 0
    js_needed = len(discovered.get("javascript", [])) > 0
    
    python_done = completion_status.get("python", not python_needed)
    js_done = completion_status.get("javascript", not js_needed)
    
    if python_done and js_done:
        # Always go to AI review for comprehensive analysis
        return "ai_review"
    elif not js_done and js_needed:
        return "javascript_analysis"
    else:
        return "ai_review"

def create_agentic_analysis_workflow() -> StateGraph:
    """Creates the complete LangGraph workflow for agentic code analysis"""
    
    # Initialize StateGraph
    workflow = StateGraph(CodeAnalysisState)
    
    # Add agent nodes
    workflow.add_node("file_discovery", file_discovery_agent)
    workflow.add_node("python_analysis", python_analysis_agent)
    workflow.add_node("ai_review", ai_review_agent)  # Comprehensive AI review
    # workflow.add_node("javascript_analysis", javascript_analysis_agent)  # TODO: Implement
    # workflow.add_node("report_synthesis", report_synthesis_agent)  # TODO: Implement
    
    # Define workflow edges with intelligent routing
    workflow.add_edge(START, "file_discovery")
    
    # Conditional routing based on discovered files
    workflow.add_conditional_edges(
        "file_discovery",
        route_language_analysis,
        {
            "python_analysis": "python_analysis",
            "javascript_analysis": END,  # TODO: Replace with actual JS agent
            "no_files": END
        }
    )
    
    # Handle analysis completion
    workflow.add_conditional_edges(
        "python_analysis",
        check_analysis_completion,
        {
            "javascript_analysis": END,  # TODO: Replace with actual JS agent
            "ai_review": "ai_review"      # Go to comprehensive AI review
        }
    )
    
    # AI review completion
    workflow.add_edge("ai_review", END)
    
    return workflow.compile()