import os
from typing import List, Annotated
from dotenv import load_dotenv
from langchain_core.messages import BaseMessage, HumanMessage, ToolMessage
from langchain_core.tools import tool
from langgraph.graph import StateGraph, START, END
from langgraph.prebuilt import ToolExecutor, ToolInvocation
from typing import TypedDict, Annotated, List
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

# --- 2. Set up the Agent State and Tool Executor ---

class AgentState(TypedDict):
    # The `add_messages` function is a helper for appending messages to the list
    messages: Annotated[list, lambda x, y: x + y]

# Create a list of the tools the agent can use
tools = [read_file_tool]
tool_executor = ToolExecutor(tools)

# --- 3. Define the Agent Logic ---

# Get the model (we'll use Gemini by default for this example)
# Make sure your GOOGLE_API_KEY is in your .env file
model = get_llm_model("gemini")
if model:
    # Bind the tools to the model, so it knows what functions it can call
    model_with_tools = model.model.bind_tools(tools)
else:
    print("⚠️ Gemini model not available. Please check your GOOGLE_API_KEY.")
    model_with_tools = None

# This is the primary node for our agent. It decides what to do.
def agent_node(state: AgentState):
    """The core of the agent. Decides whether to call a tool or finish."""
    if not model_with_tools:
        raise ValueError("Model is not initialized.")

    response = model_with_tools.invoke(state["messages"])
    
    # If the model wants to call a tool, the response will have tool_calls
    if response.tool_calls:
        return {"messages": [response]} # Pass the tool call to the next node
    else:
        # If there's no tool call, it's a final answer
        return {"messages": [response]}

# This node executes the tools that the agent decided to call
def tool_node(state: AgentState):
    """Executes the tool calls and returns the results."""
    last_message = state["messages"][-1]
    
    tool_invocations = []
    for tool_call in last_message.tool_calls:
        action = ToolInvocation(
            tool=tool_call["name"],
            tool_input=tool_call["args"],
        )
        tool_invocations.append(action)
    
    responses = tool_executor.batch(tool_invocations)
    
    tool_messages = []
    for i, tool_response in enumerate(responses):
        tool_messages.append(
            ToolMessage(content=str(tool_response), tool_call_id=last_message.tool_calls[i]['id'])
        )
        
    return {"messages": tool_messages}

# This function determines the next step after the agent node runs
def should_continue(state: AgentState):
    last_message = state["messages"][-1]
    if last_message.tool_calls:
        # If the model made a tool call, we should execute the tool
        return "tools"
    else:
        # If there are no tool calls, we're done
        return END

# --- 4. Build the Graph ---

workflow = StateGraph(AgentState)

workflow.add_node("agent", agent_node)
workflow.add_node("tools", tool_node)

workflow.add_edge(START, "agent")

# Add the conditional edge
workflow.add_conditional_edges(
    "agent",
    should_continue,
    {
        "tools": "tools",
        END: END
    }
)

workflow.add_edge("tools", "agent")

# Compile the graph into a runnable app
app = workflow.compile()

# --- 5. Run the Agent ---

if __name__ == "__main__":
    print("🤖 Agent is ready. Ask a question about a file (e.g., 'What is in pyproject.toml?'). Type 'exit' to quit.")
    
    while True:
        query = input("Human: ")
        if query.lower() == "exit":
            break
        
        # Invoke the graph with the user's message
        inputs = {"messages": [HumanMessage(content=query)]}
        
        # The `stream` method gives us real-time output as the graph runs
        for output in app.stream(inputs):
            for key, value in output.items():
                if key == "agent" and value['messages'][-1].content:
                    print(f"AI: {value['messages'][-1].content}")

        print("-" * 20)
