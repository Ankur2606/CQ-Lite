"""
Helpers for handling GitHub repository files during analysis.
"""

import os
import tempfile
from typing import Dict, List, Optional, Any

def create_temp_file_from_github_data(file_content: str, file_path: str) -> str:
    """
    Create a temporary file from GitHub file content.
    
    Args:
        file_content: Content of the file
        file_path: Original file path in GitHub repository (used for extension)
        
    Returns:
        Path to the temporary file
    """

    _, ext = os.path.splitext(file_path)
    

    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as temp_file:
        temp_file.write(file_content.encode('utf-8'))
        return temp_file.name

def find_github_file_by_path(github_files: List[Dict[str, Any]], file_path: str) -> Optional[Dict[str, Any]]:
    """
    Find a GitHub file by its path in the repository.
    
    Args:
        github_files: List of GitHub file dictionaries
        file_path: File path to find
        
    Returns:
        GitHub file dictionary or None if not found
    """
    for file in github_files:
        if file.get("file_path") == file_path:
            return file
    return None

def cleanup_temp_files(temp_files: List[str]):
    """
    Clean up temporary files created for GitHub repository analysis.
    
    Args:
        temp_files: List of temporary file paths to remove
    """
    for temp_file in temp_files:
        try:
            os.unlink(temp_file)
        except Exception as e:
            print(f"⚠️ Failed to clean up temp file {temp_file}: {e}")