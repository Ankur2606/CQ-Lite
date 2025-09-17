"""
Environment variable helper functions for the CLI.
Provides guidance on setting up required API tokens.
"""
import os
import sys
from typing import Dict, List, Optional

# Constants
DOCS_URL = "https://github.com/Ankur2606/CQ-Lite/blob/master/README.md"
REQUIRED_ENV_VARS = {
    "GOOGLE_API_KEY": {
        "purpose": "Gemini API access for AI analysis",
        "guide_url": "https://ai.google.dev/tutorials/setup"
    },
    "GITHUB_API_TOKEN": {
        "purpose": "GitHub repository access",
        "guide_url": "https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens"
    },
    "NOTION_TOKEN": {
        "purpose": "Notion integration for report generation",
        "guide_url": "https://developers.notion.com/docs/getting-started"
    },
    "NOTION_PAGE_ID": {
        "purpose": "Target Notion page for report generation",
        "guide_url": "https://developers.notion.com/docs/working-with-page-content"
    },
    "NEBIUS_API_KEY": {
        "purpose": "Alternative AI model access",
        "guide_url": ""
    }
}

class MissingEnvVarError(Exception):
    """Exception raised for missing required environment variables."""
    pass

def get_missing_env_vars(required_vars: List[str]) -> List[str]:
    """
    Check for missing environment variables.
    
    Args:
        required_vars: List of environment variables to check
        
    Returns:
        List of missing environment variables
    """
    missing = []
    for var in required_vars:
        if not os.environ.get(var):
            missing.append(var)
    return missing

def check_env_vars(required_vars: List[str], raise_error: bool = True) -> bool:
    """
    Check if required environment variables are set.
    
    Args:
        required_vars: List of required environment variables
        raise_error: Whether to raise an error if variables are missing
        
    Returns:
        True if all variables are set, False otherwise
        
    Raises:
        MissingEnvVarError: If variables are missing and raise_error is True
    """
    missing = get_missing_env_vars(required_vars)
    
    if missing:
        if raise_error:
            raise MissingEnvVarError(f"Missing required environment variables: {', '.join(missing)}")
        return False
    
    return True

def print_env_var_help(missing_vars: List[str], feature_name: Optional[str] = None):
    """
    Print helpful instructions for setting up environment variables.
    
    Args:
        missing_vars: List of missing environment variables
        feature_name: Optional name of the feature requiring these variables
    """
    if feature_name:
        print(f"\n❌ Cannot use {feature_name} feature due to missing environment variables.")
    else:
        print("\n❌ Missing required environment variables.")
    
    print("\nPlease set the following environment variables:\n")
    
    # Get shell type
    shell = os.environ.get("SHELL", "").lower()
    is_windows = sys.platform.startswith("win")
    
    # Determine export command based on shell
    if is_windows:
        export_cmd = "$env:"  # PowerShell
        example = 'In PowerShell: $env:GOOGLE_API_KEY="your-api-key-here"'
    else:
        export_cmd = "export "  # Bash/Zsh
        example = 'In Bash/Zsh: export GOOGLE_API_KEY="your-api-key-here"'
    
    # Print instructions for each missing variable
    for var in missing_vars:
        info = REQUIRED_ENV_VARS.get(var, {"purpose": "Required for operation"})
        print(f"  {var}:")
        print(f"    Purpose: {info['purpose']}")
        print(f"    Command: {export_cmd}{var}=\"your-{var.lower()}-here\"")
        if info.get("guide_url"):
            print(f"    More info: {info['guide_url']}")
        print("")
    
    # Print example for .env file
    print("Or add to your .env file in the project root:\n")
    for var in missing_vars:
        print(f"{var}=your-{var.lower()}-here")
    
    print(f"\nFor more information, please refer to: {DOCS_URL}")

def check_github_token(raise_error: bool = False) -> bool:
    """
    Check if GitHub API token is set for repository analysis.
    
    Args:
        raise_error: Whether to raise an error if token is missing
        
    Returns:
        True if token is set, False otherwise
    """
    if not os.environ.get("GITHUB_API_TOKEN"):
        if raise_error:
            raise MissingEnvVarError("GitHub API token is required for repository analysis")
        print_env_var_help(["GITHUB_API_TOKEN"], "GitHub repository analysis")
        return False
    return True

def check_notion_credentials(raise_error: bool = False) -> bool:
    """
    Check if Notion credentials are set for report generation.
    
    Args:
        raise_error: Whether to raise an error if credentials are missing
        
    Returns:
        True if credentials are set, False otherwise
    """
    required = ["NOTION_TOKEN", "NOTION_PAGE_ID"]
    missing = get_missing_env_vars(required)
    
    if missing:
        if raise_error:
            raise MissingEnvVarError(f"Notion credentials are required for report generation: {', '.join(missing)}")
        print_env_var_help(missing, "Notion report generation")
        return False
    return True

def check_ai_credentials(model: str = "gemini", raise_error: bool = False) -> bool:
    """
    Check if AI API credentials are set for the specified model.
    
    Args:
        model: AI model to check credentials for (gemini or nebius)
        raise_error: Whether to raise an error if credentials are missing
        
    Returns:
        True if credentials are set, False otherwise
    """
    required = []
    
    if model.lower() == "gemini":
        required = ["GOOGLE_API_KEY"]
    elif model.lower() == "nebius":
        required = ["NEBIUS_API_KEY"]
    
    missing = get_missing_env_vars(required)
    
    if missing:
        if raise_error:
            raise MissingEnvVarError(f"AI API credentials are required for {model} model: {', '.join(missing)}")
        print_env_var_help(missing, f"{model.capitalize()} AI analysis")
        return False
    return True