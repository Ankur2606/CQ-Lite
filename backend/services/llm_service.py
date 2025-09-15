from typing import Union, Optional
from backend.services.gemini_service import get_gemini_model, GeminiModel
from backend.services.nebius_service import get_nebius_model, NebiusModel

# Define a type hint for the model that can be either Gemini or Nebius
LLMModel = Union[GeminiModel, NebiusModel]

def get_llm_model(model_choice: str) -> Optional[LLMModel]:
    """
    Factory function to get the appropriate LLM model based on the user's choice.

    Args:
        model_choice: The name of the model to use ('gemini' or 'nebius').

    Returns:
        An instance of the selected model wrapper (GeminiModel or NebiusModel),
        or None if the choice is invalid or the model is not configured.
    """
    if model_choice == 'gemini':
        print("✅ Using Gemini model for AI analysis.")
        return get_gemini_model()
    elif model_choice == 'nebius':
        print("✅ Using Nebius model for AI analysis.")
        model = get_nebius_model()
        if not model:
            print("⚠️ Nebius model is not configured. Please set the NEBIUS_API_KEY.")
        return model
    else:
        print(f"❌ Invalid model choice: {model_choice}. Defaulting to None.")
        return None
