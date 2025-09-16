from typing import List, Dict, Any
from backend.tools.vector_store_tool import query_vector_store
from backend.services.llm_service import get_llm_model

def qna_agent_for_code(query: str, history: List[Dict[str, str]]) -> Dict[str, Any]:
    """
    Answers questions about the codebase using vector store retrieval and an LLM.
    
    Args:
        query (str): The user's question.
        history (List[Dict[str, str]]): The conversation history.

    Returns:
        Dict[str, Any]: A dictionary containing the answer, sources, and raw retrievals.
    """
    print(f"🧠 Q&A agent received query: {query}")

    # 1. Retrieve relevant code chunks from the vector store
    retrievals = query_vector_store(query, n_results=6)
    print(f"   Found {len(retrievals)} relevant document(s) in vector store.")

    # 2. Assemble the prompt for the LLM
    system_prompt = """You are a principal software architect and expert code reviewer. Your task is to answer questions about a codebase based *exclusively* on the provided code snippets and conversation history. When answering, adhere to the following principles:
1. **Fact-Based Analysis**: Ground all answers in the provided context. Do not invent or assume functionality.
2. **Technical Precision**: Use precise terminology. Your answers should be technically sound and unambiguous.
3. **Conciseness**: Address the user's query directly without unnecessary preamble.
4. **Objectivity**: Maintain a neutral, professional tone. Your goal is to inform, not to opine."""
    
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    
    context_str = ""
    sources = set()
    for i, retrieval in enumerate(retrievals):
        if "document" in retrieval and "metadata" in retrieval:
            file_path = retrieval['metadata'].get('file_path', 'unknown file')
            sources.add(file_path)
            context_str += f"--- Context {i+1}: {file_path} ---\n"
            context_str += f"{retrieval['document']}\n\n"

    full_prompt = f"{system_prompt}\n\n--- Conversation History ---\n{history_str}\n\n--- Retrieved Code Context ---\n{context_str}\n\n--- User Query ---\n{query}\n\nBased on the provided context, please answer the user's query."

    # 3. Call the LLM to generate an answer
    llm_model = get_llm_model("gemini") # Temperature is handled in the service
    
    answer = "Could not generate an answer."
    if llm_model:
        try:
            print("   Generating answer with LLM...")
            ai_response = llm_model.generate_content(full_prompt)
            answer = ai_response.text
            print("   ✅ LLM answer generated.")
        except Exception as e:
            answer = f"Error generating answer from LLM: {e}"
            print(f"   ❌ {answer}")
    else:
        answer = "LLM model not available."
        print(f"   ⚠️ {answer}")

    # 4. Format and return the response
    return {
        "answer": answer,
        "sources": list(sources),
        "retrievals": retrievals
    }

if __name__ == '__main__':
    # Example usage for direct testing
    print("--- Testing Q&A Agent ---")
    test_query = "what issues are there in my code ?"
    test_history = [
        {"role": "user", "content": "hello"},
        {"role": "assistant", "content": "Hi! How can I help you with your code?"}
    ]
    
    result = qna_agent_for_code(test_query, test_history)
    
    print("\n--- Agent Response ---")
    print(f"Answer: {result['answer']}")
    print(f"Sources: {result['sources']}")
    print("----------------------")
