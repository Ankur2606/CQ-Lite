from langgraph.graph import StateGraph, START, END
from .state_schema import CodeAnalysisState
from .file_discovery_agent import file_discovery_agent
from .python_analysis_agent import python_analysis_agent
from .ai_review_agent import ai_review_agent
from .qna_agent import qna_agent_for_code
from .notion_report_agent import notion_report_agent
import re

def detect_analysis_request(query: str) -> dict:
    """
    Detect if the user is requesting code analysis in their query.
    Returns dict with 'is_analysis' bool and extracted parameters.
    """
    query_lower = query.lower()
    
    # Patterns to detect analysis requests
    analysis_patterns = [
        r"analyze\s+(?:the\s+)?(?:codebase|folder|directory|path)?\s*(?:at|in|of)?\s*([^\s]+)",
        r"review\s+(?:the\s+)?(?:codebase|folder|directory|path)?\s*(?:at|in|of)?\s*([^\s]+)",
        r"check\s+(?:the\s+)?(?:codebase|folder|directory|path)?\s*(?:at|in|of)?\s*([^\s]+)",
        r"examine\s+(?:the\s+)?(?:codebase|folder|directory|path)?\s*(?:at|in|of)?\s*([^\s]+)",
        r"scan\s+(?:the\s+)?(?:codebase|folder|directory|path)?\s*(?:at|in|of)?\s*([^\s]+)",
    ]
    
    for pattern in analysis_patterns:
        match = re.search(pattern, query_lower)
        if match:
            path = match.group(1).strip()
            # Extract model if specified
            model_match = re.search(r"(?:using|with)\s+(?:model\s+)?([^\s]+)", query_lower)
            model = model_match.group(1) if model_match else "gemini"
            
            return {
                "is_analysis": True,
                "path": path,
                "model": model
            }
    
    return {"is_analysis": False}

def qna_agent_wrapper(state: CodeAnalysisState) -> CodeAnalysisState:
    """
    Wrapper for Q&A agent that handles both regular Q&A and analysis triggering.
    """
    current_query = state.get("current_query", "")
    conversation_history = state.get("conversation_history", [])
    
    # Convert LangChain messages to the format expected by qna_agent
    history = []
    for msg in conversation_history:
        if hasattr(msg, 'type'):
            role = msg.type
        else:
            role = "user" if msg.get("role") == "user" else "assistant"
        content = msg.content if hasattr(msg, 'content') else str(msg.get("content", ""))
        history.append({"role": role, "content": content})
    
    # Detect if this is an analysis request
    detection = detect_analysis_request(current_query)
    
    if detection["is_analysis"]:
        # Update state to trigger analysis
        state["analysis_requested"] = True
        state["detected_analysis_path"] = detection["path"]
        state["detected_model_choice"] = detection["model"]
        state["current_step"] = "analysis_triggered"
        
        # Provide response about triggering analysis
        answer = f"I'll analyze the codebase at '{detection['path']}' using the {detection['model']} model. Starting analysis now..."
    else:
        # Regular Q&A
        result = qna_agent_for_code(current_query, history)
        answer = result.get("answer", "I couldn't generate an answer.")
        state["analysis_context"] = {
            "sources": result.get("sources", []),
            "retrievals": result.get("retrievals", [])
        }
    
    # Update conversation history with the response
    from langchain_core.messages import AIMessage
    response_message = AIMessage(content=answer)
    state["conversation_history"].append(response_message)
    
    return state

def route_workflow_start(state: CodeAnalysisState) -> str:
    """Route between chat mode and analysis mode at workflow start"""
    if state.get("chat_mode", False):
        return "qna_agent"
    else:
        return "file_discovery"

def route_after_qna(state: CodeAnalysisState) -> str:
    """Route after Q&A agent - either trigger analysis or end"""
    if state.get("analysis_requested", False):
        return "file_discovery"
    else:
        return END

def route_after_ai_review(state: CodeAnalysisState) -> str:
    """Route after AI review - either push to Notion or end"""
    if state.get("notion_reporting_enabled", False):
        return "notion_report"
    else:
        return END

def route_language_analysis(state: CodeAnalysisState) -> str:
    """AI-driven routing based on analysis strategy"""
    strategy = state.get("analysis_strategy", {})
    discovered = state.get("discovered_files", {})
    
    has_python = len(discovered.get("python", [])) > 0
    has_js = len(discovered.get("javascript", [])) > 0
    has_docker = len(discovered.get("docker", [])) > 0
    
    if not has_python and not has_js and not has_docker:
        return "no_files"
    
    # Use AI strategy to determine routing
    if strategy.get("parallel_processing", False) and has_python and has_js:
        return "python_analysis"  # Start with Python, JS will follow
    elif strategy.get("python_priority", True) and has_python:
        return "python_analysis"
    elif has_js:
        return "javascript_analysis"
    elif has_docker:
        return "docker_analysis"
    else:
        return "no_files"

def check_analysis_completion(state: CodeAnalysisState) -> str:
    """Check if all required analysis is complete"""
    completion_status = state.get("file_analysis_complete", {})
    discovered = state.get("discovered_files", {})
    
    python_needed = len(discovered.get("python", [])) > 0
    js_needed = len(discovered.get("javascript", [])) > 0
    docker_needed = len(discovered.get("docker", [])) > 0
    
    python_done = completion_status.get("python", not python_needed)
    js_done = completion_status.get("javascript", not js_needed)
    docker_done = completion_status.get("docker", not docker_needed)
    
    if python_done and js_done and docker_done:
        # Always go to AI review for comprehensive analysis
        return "ai_review"
    elif not js_done and js_needed:
        return "javascript_analysis"
    elif not docker_done and docker_needed:
        return "docker_analysis"
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
    workflow.add_node("qna_agent", qna_agent_wrapper)  # Q&A agent for chat mode
    workflow.add_node("notion_report", notion_report_agent)  # Notion reporting agent
    
    # Import and add JavaScript analysis agent
    from .javascript_analysis_agent import javascript_analysis_agent
    workflow.add_node("javascript_analysis", javascript_analysis_agent)
    
    # Import and add Docker analysis agent
    from .docker_analysis_agent import docker_analysis_agent
    workflow.add_node("docker_analysis", docker_analysis_agent)
    
    # workflow.add_node("report_synthesis", report_synthesis_agent)  # TODO: Implement
    
    # Define workflow edges with intelligent routing
    workflow.add_conditional_edges(
        START,
        route_workflow_start,
        {
            "qna_agent": "qna_agent",
            "file_discovery": "file_discovery"
        }
    )
    
    # Q&A agent routing
    workflow.add_conditional_edges(
        "qna_agent",
        route_after_qna,
        {
            "file_discovery": "file_discovery",
            END: END
        }
    )
    
    # Conditional routing based on discovered files
    workflow.add_conditional_edges(
        "file_discovery",
        route_language_analysis,
        {
            "python_analysis": "python_analysis",
            "javascript_analysis": "javascript_analysis",
            "docker_analysis": "docker_analysis",
            "no_files": END
        }
    )
    
    # Handle analysis completion
    workflow.add_conditional_edges(
        "python_analysis",
        check_analysis_completion,
        {
            "javascript_analysis": "javascript_analysis",
            "docker_analysis": "docker_analysis",
            "ai_review": "ai_review"      # Go to comprehensive AI review
        }
    )
    
    # Add edges for JavaScript and Docker analysis
    workflow.add_conditional_edges(
        "javascript_analysis",
        check_analysis_completion,
        {
            "docker_analysis": "docker_analysis",
            "ai_review": "ai_review"
        }
    )
    
    # Add edge from Docker analysis to AI review
    workflow.add_edge("docker_analysis", "ai_review")
    
    # AI review to Notion routing
    workflow.add_conditional_edges(
        "ai_review",
        route_after_ai_review,
        {
            "notion_report": "notion_report",
            END: END
        }
    )
    
    # Notion report completion
    workflow.add_edge("notion_report", END)
    
    return workflow.compile()