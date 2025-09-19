"""
GitHub repository content fetching tools.
This module provides functionality to fetch and process files from GitHub repositories.
"""

import os
import re
import base64
import requests
from typing import List, Dict, Optional, Any, Tuple
from urllib.parse import urlparse
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# GitHub API endpoints
GITHUB_API_BASE = "https://api.github.com"
GITHUB_CONTENT_API = GITHUB_API_BASE + "/repos/{owner}/{repo}/contents/{path}"

# File type filters
CODE_EXTENSIONS = {

    '.py', '.pyx', '.pyw', '.ipynb',

    '.js', '.jsx', '.ts', '.tsx', '.mjs', '.cjs',

    '.html', '.htm', '.css', '.scss', '.sass', '.less',

    '.json', '.yml', '.yaml', '.toml', '.ini', '.xml',

    '.dockerfile', '.dockerignore',

    '.c', '.cpp', '.h', '.hpp', '.cs', '.java', '.go', '.rb', '.php',
    '.rs', '.swift', '.kt', '.md', '.rst', '.txt'
}

class GitHubAPIException(Exception):
    """Exception raised for errors in the GitHub API interactions."""
    pass

def parse_github_url(repo_url: str) -> Dict[str, str]:
    """
    Parse a GitHub repository URL to extract owner and repo name.
    
    Args:
        repo_url: GitHub repository URL
        
    Returns:
        Dict containing 'owner' and 'repo' keys
        
    Raises:
        ValueError: If the URL is not a valid GitHub repository URL
    """

    repo_url = repo_url.strip()
    




    
    if repo_url.startswith("git@github.com:"):
    
        path = repo_url.split("git@github.com:")[1]
        if path.endswith(".git"):
            path = path[:-4]  # Remove .git suffix
        parts = path.split("/")
        if len(parts) >= 2:
            return {"owner": parts[0], "repo": parts[1]}
    else:
    
        parsed_url = urlparse(repo_url)
        if parsed_url.netloc in ("github.com", "www.github.com"):
            path_parts = parsed_url.path.strip("/").split("/")
            if len(path_parts) >= 2:
                owner = path_parts[0]
                repo = path_parts[1]
                if repo.endswith(".git"):
                    repo = repo[:-4]  # Remove .git suffix
                return {"owner": owner, "repo": repo}
    
    raise ValueError(f"Invalid GitHub repository URL: {repo_url}")

def is_code_file(file_path: str) -> bool:
    """
    Check if a file is a code file based on its extension.
    
    Args:
        file_path: Path to the file
        
    Returns:
        True if the file is a code file, False otherwise
    """
    _, ext = os.path.splitext(file_path.lower())
    return ext in CODE_EXTENSIONS

def is_size_acceptable(size_bytes: int, max_size_mb: float = 1.0) -> bool:
    """
    Check if the file size is within acceptable limits.
    
    Args:
        size_bytes: Size of the file in bytes
        max_size_mb: Maximum acceptable size in megabytes
        
    Returns:
        True if the size is acceptable, False otherwise
    """
    return size_bytes <= (max_size_mb * 1024 * 1024)

def fetch_repo_contents(owner: str, repo: str, path: str = "", token: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Fetch the contents of a repository directory.
    
    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        path: Path within the repository (default: root)
        token: GitHub API token (optional)
        
    Returns:
        List of dictionaries representing files and directories
        
    Raises:
        GitHubAPIException: If the API request fails
    """
    url = GITHUB_CONTENT_API.format(owner=owner, repo=repo, path=path)
    
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        error_msg = f"GitHub API error: {response.status_code} - {response.text}"
        print(f"Error accessing {url}: {error_msg}")
        raise GitHubAPIException(error_msg)
    
    return response.json()

def fetch_file_content(file_url: str, token: Optional[str] = None) -> str:
    """
    Fetch the content of a file from GitHub.
    
    Args:
        file_url: GitHub API URL for the file
        token: GitHub API token (optional)
        
    Returns:
        The content of the file as a string
        
    Raises:
        GitHubAPIException: If the API request fails
    """
    headers = {"Accept": "application/vnd.github.v3+json"}
    if token:
        headers["Authorization"] = f"token {token}"
    
    response = requests.get(file_url, headers=headers)
    
    if response.status_code != 200:
        raise GitHubAPIException(f"GitHub API error: {response.status_code} - {response.text}")
    
    data = response.json()
    
    if data.get("encoding") == "base64":
        content = base64.b64decode(data.get("content", "")).decode("utf-8")
        
    
        line_count = content.count('\n') + 1
        if line_count > 500:
            print(f"Skipping large file ({line_count} lines): {data.get('path', 'unknown')}")
            return f"# File too large: {line_count} lines (max 500)\n"
        
        return content
    else:
        raise GitHubAPIException(f"Unsupported encoding: {data.get('encoding')}")

def fetch_repo_files_recursive(owner: str, repo: str, path: str = "", token: Optional[str] = None, 
                              max_files: int = 100, current_count: int = 0) -> Tuple[List[Dict[str, Any]], int]:
    """
    Recursively fetch files from a GitHub repository.
    
    Args:
        owner: GitHub repository owner
        repo: GitHub repository name
        path: Path within the repository (default: root)
        token: GitHub API token (optional)
        max_files: Maximum number of files to fetch
        current_count: Current file count
        
    Returns:
        Tuple of (list of dictionaries with file information, updated file count)
    """
    results = []
    

    if current_count >= max_files:
        print(f"Reached maximum file count ({max_files})")
        return results, current_count
    
    try:
        print(f"📁 Exploring directory: {path if path else 'root'}")
        contents = fetch_repo_contents(owner, repo, path, token)
        
    
        if not isinstance(contents, list):
            contents = [contents]
        
    
        contents.sort(key=lambda x: (
            x.get("type") != "dir",  # Directories first
            x.get("name", "").lower() not in ["src", "lib", "portia", "app"],  # Common source dirs first
            not x.get("path", "").endswith(".py"),  # Python files first within files
            x.get("name", "").lower()
        ))
        
        for item in contents:
        
            if current_count >= max_files:
                break
                
            item_type = item.get("type")
            item_path = item.get("path", "")
            item_name = item.get("name", "")
            item_size = item.get("size", 0)
            
        
            if item_path.startswith(".git/") or item_name in [".git", "node_modules", "__pycache__", "venv", ".venv", "env"]:
                continue
                
            if item_type == "dir":
                print(f"📂 Entering directory: {item_path}")
            
                sub_results, current_count = fetch_repo_files_recursive(
                    owner, repo, item_path, token, max_files, current_count
                )
                results.extend(sub_results)
                
            elif item_type == "file" and is_code_file(item_path) and is_size_acceptable(item_size):
            
                if current_count >= max_files:
                    break
                    
                try:
                    content = fetch_file_content(item.get("url", ""), token)
                    
                
                    results.append({
                        "file_path": item_path,
                        "content": content,
                        "size": item_size,
                        "sha": item.get("sha", ""),
                        "url": item.get("html_url", "")
                    })
                    current_count += 1
                    print(f"✅ Fetched file {current_count}/{max_files}: {item_path}")
                    
                except GitHubAPIException as e:
                    print(f"Error fetching file {item_path}: {e}")
                except Exception as e:
                    print(f"Unexpected error processing file {item_path}: {e}")
            else:
            
                if not is_code_file(item_path):
                    print(f"⏭️ Skipping non-code file: {item_path}")
                elif not is_size_acceptable(item_size):
                    print(f"⏭️ Skipping large file ({item_size/1024/1024:.2f} MB): {item_path}")
                    
    except GitHubAPIException as e:
        print(f"Error fetching directory {path}: {e}")
    except Exception as e:
        print(f"Unexpected error processing directory {path}: {e}")
        
    return results, current_count

def fetch_repo_files(repo_url: str, token: Optional[str] = None, max_files: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch files from a GitHub repository given its URL.
    
    Args:
        repo_url: GitHub repository URL
        token: GitHub API token (optional)
        max_files: Maximum number of files to fetch (default: 100)
        
    Returns:
        List of dictionaries with file information
        
    Raises:
        ValueError: If the URL is invalid
        GitHubAPIException: If the API request fails
    """
    print(f"Fetching GitHub repository: {repo_url}")
    

    if token is None:
        token = os.environ.get("GITHUB_API_TOKEN")
        if token:
            print("Using GitHub token from environment variable")
        else:
            print("No GitHub token provided. Requests may be rate-limited.")
    

    repo_info = parse_github_url(repo_url)
    owner = repo_info["owner"]
    repo = repo_info["repo"]
    
    print(f"Repository: {owner}/{repo}")
    

    files, final_count = fetch_repo_files_recursive(owner, repo, "", token, max_files)
    print(f"Successfully fetched {final_count} files from repository")
    return files