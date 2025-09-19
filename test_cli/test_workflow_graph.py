import asyncio
from pathlib import Path
import sys

# Add the parent directory to the path so we can import backend modules
sys.path.append(str(Path(__file__).parent.parent))

from backend.agents.workflow import create_agentic_analysis_workflow

def generate_workflow_graph_ascii():
    """
    Prints an ASCII representation of the agentic analysis workflow graph.
    """
    print("🤖 Initializing agentic workflow to generate ASCII graph...")
    

    agentic_workflow = create_agentic_analysis_workflow()
    
    print("\n📊 Workflow Graph (ASCII Representation):")
    
    try:
    
        agentic_workflow.get_graph().print_ascii()
        
        print("\n✅ Successfully printed the workflow graph.")
        print("The diagram above shows the nodes and edges of your agentic workflow.")
        
    except Exception as e:
        print(f"❌ An error occurred while generating the ASCII graph: {e}")

if __name__ == "__main__":
    generate_workflow_graph_ascii()
