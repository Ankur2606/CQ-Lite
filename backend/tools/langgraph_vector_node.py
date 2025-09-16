from typing import Dict, Any
from langchain_core.tools import tool
from langgraph.prebuilt import ToolNode
from backend.tools.vector_store_tool import add_to_vector_store

@tool
def add_to_vector_store_tool(file_path: str, description: str, code: str, metadata: Dict[str, Any]) -> str:
    """Adds a document chunk to the vector store."""
    print(f"--- Calling vector store tool for: {file_path} ---")
    try:
        payload = {
            "file_path": file_path,
            "description": description,
            "code": code,
            "metadata": metadata
        }
        add_to_vector_store.invoke(payload)
        return f"Successfully added chunk from {file_path} to vector store."
    except Exception as e:
        return f"Error adding to vector store: {e}"

# Create a list of the tools, in this case just one
vector_tools = [add_to_vector_store_tool]

# Create the ToolNode
vector_store_node = ToolNode(vector_tools)
