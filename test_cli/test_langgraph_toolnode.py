import os
from typing import List, Annotated
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolNode, tools_condition
from typing import TypedDict
from backend.services.llm_service import get_llm_model

# Load environment variables from .env file
load_dotenv()

# --- 1. Define Your Tools ---

@tool
def read_file_tool(file_path: str) -> str:
    """Reads the content of a file at the given path and returns it as a string."""
    print(f"--- Calling read_file_tool with: {file_path} ---")
    try:
        # For safety, prevent reading files outside the current directory
        if ".." in file_path:
            return "Error: Directory traversal is not allowed."
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        return f"Error reading file: {e}"

# --- 2. Set up the Agent State ---

class AgentState(TypedDict):
    messages: Annotated[list, lambda x, y: x + y]

# Create a list of the tools the agent can use
tools = [read_file_tool]

# --- 3. Define the Agent Logic and Graph ---

# Get the model and bind the tools
model = get_llm_model("gemini")
if model:
    model_with_tools = model.model.bind_tools(tools)
else:
    print("⚠️ Gemini model not available. Please check your GOOGLE_API_KEY.")
    model_with_tools = None

# Define the node that will call the LLM
def tool_calling_llm(state: AgentState):
    """Node that invokes the LLM to decide on an action or respond."""
    if not model_with_tools:
        raise ValueError("Model is not initialized.")
    
    response = model_with_tools.invoke(state["messages"])
    return {"messages": [response]}

# --- 4. Build the Graph using Pre-built Components ---

# Initialize the graph
builder = StateGraph(AgentState)

# Add the node that calls the LLM
builder.add_node("tool_calling_llm", tool_calling_llm)

# Add the pre-built ToolNode. This node automatically executes any tools
# that the LLM decides to call.
builder.add_node("tools", ToolNode(tools))

# Set the entry point of the graph
builder.add_edge(START, "tool_calling_llm")

# Add the conditional edge. This uses the pre-built `tools_condition`
# to check if the LLM's last response was a tool call.
builder.add_conditional_edges(
    "tool_calling_llm",
    tools_condition,
    # If the condition is "tools", it routes to the "tools" node.
    # If the condition is "end", it routes to the END node.
    {
        "tools": "tools",
        END: END
    }
)

# After the tools are executed, the flow should go back to the LLM
# so it can process the tool's output.
builder.add_edge("tools", "tool_calling_llm")

# Compile the graph
graph = builder.compile()

# --- 5. Run the Agent ---

if __name__ == "__main__":
    print("🤖 Simple Agent is ready. Ask a question about a file (e.g., 'What is in pyproject.toml?'). Type 'exit' to quit.")
    
    while True:
        query = input("Human: ")
        if query.lower() == "exit":
            break
        
        # Invoke the graph with the user's message
        inputs = {"messages": [HumanMessage(content=query)]}
        
        # The `stream` method gives us real-time output as the graph runs
        for output in graph.stream(inputs):
            for key, value in output.items():
                # We only want to print the final response from the AI
                if key == "tool_calling_llm" and not value['messages'][-1].tool_calls:
                    print(f"AI: {value['messages'][-1].content}")

        print("-" * 20)
