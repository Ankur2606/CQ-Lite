"""
Command-line interface for starting the API server
"""

import argparse
import sys
from pathlib import Path
import os

# Add the project root to path
sys.path.append(str(Path(__file__).parent.parent))

# Import the API server
from api.main import app

def main():
    """
    Command-line entry point for starting the API server
    """
    parser = argparse.ArgumentParser(
        description="Start the CQ Lite API server"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="Port to run the API server on (default: 8000)",
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to run the API server on (default: 0.0.0.0)",
    )
    parser.add_argument(
        "--reload",
        action="store_true",
        help="Enable auto-reload for development",
    )
    
    args = parser.parse_args()
    

    print(f"Starting API server at http://{args.host}:{args.port}")
    

    import uvicorn
    import datetime
    
    uvicorn.run(
        "api.main:app",
        host=args.host,
        port=args.port,
        reload=args.reload,
    )

if __name__ == "__main__":
    main()