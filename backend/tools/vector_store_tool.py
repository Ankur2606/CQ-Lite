import chromadb
from openai import OpenAI
from langchain_core.tools import tool
from typing import List, Dict, Any
import os
from dotenv import load_dotenv
from chromadb.api.types import Documents, EmbeddingFunction

load_dotenv()

# --- Custom Embedding Function Wrapper ---
class CustomEmbeddingFunction(EmbeddingFunction):
    """A custom wrapper to make a direct OpenAI client compatible with ChromaDB."""
    def __init__(self, client: OpenAI, model_name: str = "Qwen/Qwen3-Embedding-8B"):
        self._client = client
        self._model_name = model_name

    def __call__(self, input: Documents) -> list[list[float]]:
        """Embeds documents using the underlying OpenAI client."""
        response = self._client.embeddings.create(model=self._model_name, input=input)
        return [item.embedding for item in response.data]

# --- Constants ---
# Use a persistent directory for the ChromaDB instance
# Ensure the directory exists
CHROMA_DB_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "db", "chroma_db")
os.makedirs(CHROMA_DB_PATH, exist_ok=True)

COLLECTION_NAME = "codebase_collection"

# --- Embedding Model ---
def get_embedding_model() -> CustomEmbeddingFunction:
    """Initializes and returns a ChromaDB-compatible embedding function for Nebius AI."""
    # Ensure the API key is set in the environment
    if "NEBIUS_API_KEY" not in os.environ:
        raise ValueError("NEBIUS_API_KEY environment variable not set.")
    
    # Instantiate the OpenAI client for Nebius AI
    client = OpenAI(
        base_url="https://api.studio.nebius.com/v1/",
        api_key=os.environ.get("NEBIUS_API_KEY")
    )
    
    # Return the custom function wrapper
    return CustomEmbeddingFunction(client)

# --- ChromaDB Client ---
def get_chroma_client():
    """Initializes and returns a persistent ChromaDB client."""
    return chromadb.PersistentClient(path=CHROMA_DB_PATH)

def _sanitize_metadata(metadata: Dict[str, Any]) -> Dict[str, Any]:
    """Converts list values in metadata to comma-separated strings."""
    sanitized = {}
    for key, value in metadata.items():
        if isinstance(value, list):
            sanitized[key] = ", ".join(map(str, value))
        else:
            sanitized[key] = value
    return sanitized

# --- Tool Definition ---
@tool
def add_to_vector_store(
    file_path: str,
    description: str,
    code: str,
    metadata: Dict[str, Any]
) -> str:
    """
    Adds file information, code, and metadata to the ChromaDB vector store.

    Args:
        file_path (str): The path of the file being processed.
        description (str): A summary of the file's purpose, functions, and classes.
        code (str): The full content of the file.
        metadata (Dict[str, Any]): A dictionary of metadata about the file.

    Returns:
        str: A confirmation message indicating success or failure.
    """
    print(f"--- Calling add_to_vector_store for: {file_path} ---")
    try:
        embedding_model = get_embedding_model()
        client = get_chroma_client()
        
        # Get or create the collection
        collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_model
        )

        # The document to be embedded and stored
        document_content = f"Description: {description}\n\nCode:\n{code}"
        
        # The ID for the document will be the file path to ensure uniqueness
        doc_id = file_path

        # Sanitize metadata before adding
        sanitized_metadata = _sanitize_metadata(metadata)

        # Add the document to the collection
        collection.add(
            ids=[doc_id],
            documents=[document_content],
            metadatas=[sanitized_metadata]
        )
        
        print(f"✅ Successfully added '{file_path}' to vector store.")
        return f"Successfully added '{file_path}' to vector store."

    except Exception as e:
        error_message = f"Error adding to vector store: {e}"
        print(f"❌ {error_message}")
        return error_message

# --- Utility function to query the vector store (for the Q&A agent) ---
def query_vector_store(query: str, n_results: int = 5) -> List[Dict[str, Any]]:
    """
    Queries the vector store for documents related to the user's query.
    """
    try:
        embedding_model = get_embedding_model()
        client = get_chroma_client()
        collection = client.get_collection(
            name=COLLECTION_NAME,
            embedding_function=embedding_model
        )

        results = collection.query(
            query_texts=[query],
            n_results=n_results
        )

        # Format the results to be more useful
        formatted_results = []
        if results and results.get("documents"):
            for i, doc in enumerate(results["documents"][0]):
                formatted_results.append({
                    "document": doc,
                    "metadata": results["metadatas"][0][i],
                    "distance": results["distances"][0][i]
                })
        
        return formatted_results

    except Exception as e:
        print(f"❌ Error querying vector store: {e}")
        return [{"error": str(e)}]

if __name__ == '__main__':
    # Example usage for testing the tool directly
    print("Testing vector store tool...")
    
    # Mock data based on the desired schema
    mock_metadata = {
        "file_path": "src/utils/parser.py",
        "file_type": ".py",
        "module": "utils",
        "functions": ["parse_json", "clean_data"],
        "classes": ["Parser"],
        "num_lines": 240,
        "commit_hash": "a1b2c3d", # Example data
        "last_modified": "2025-09-16T14:00:00Z" # Example data
    }
    
    mock_description = "A utility module for parsing and cleaning data. Contains the Parser class."
    mock_code = 'class Parser:\n    def parse_json(self, data):\n        return json.loads(data)'

    # Test adding to the store
    add_result = add_to_vector_store.invoke({
        "file_path": "src/utils/parser.py",
        "description": mock_description,
        "code": mock_code,
        "metadata": mock_metadata
    })
    print(f"Add Result: {add_result}")

    # Test querying the store
    print("\nQuerying for 'parser'...")
    query_results = query_vector_store("parser")
    print(f"Query Results: {query_results}")
