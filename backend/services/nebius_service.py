import os
from openai import OpenAI
from typing import Optional

_client: Optional[OpenAI] = None

def get_nebius_client() -> OpenAI:
    """
    Initializes and returns a singleton OpenAI client for Nebius AI.
    """
    global _client
    if _client is None:
        api_key = os.environ.get("NEBIUS_API_KEY")
        if not api_key:
        
        
            print("⚠️ NEBIUS_API_KEY environment variable not set. Nebius AI will not be available.")
            return None
        
        _client = OpenAI(
            base_url="https://api.studio.nebius.com/v1/",
            api_key=api_key
        )
    return _client

class NebiusModel:
    """
    A wrapper for the Nebius AI model to provide a consistent interface
    with the Gemini model wrapper.
    """
    def __init__(self):
        self.client = get_nebius_client()
        self.model = "openai/gpt-oss-120b"
    

    def generate_content(self, prompt: str) -> 'NebiusResponse':
        """
        Generates content using the Nebius AI model.
        """
        if not self.client:
            raise ValueError("Nebius client is not initialized. Please set the NEBIUS_API_KEY environment variable.")

    
    
        system_prompt = "You are a world-class expert code analysis AI. Follow the user's instructions carefully and provide your response in the requested format."
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ]
        )
        return NebiusResponse(response)

class NebiusResponse:
    """
    A simple wrapper to mimic the structure of the Gemini response object,
    providing a `text` attribute.
    """
    def __init__(self, completion):
        if completion.choices:
            self.text = completion.choices[0].message.content or ""
        else:
            self.text = ""

_nebius_model: Optional[NebiusModel] = None

def get_nebius_model() -> Optional[NebiusModel]:
    """
    Returns a singleton instance of the NebiusModel.
    """
    global _nebius_model
    if _nebius_model is None:
        if os.environ.get("NEBIUS_API_KEY"):
            _nebius_model = NebiusModel()
    return _nebius_model
