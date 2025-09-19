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
    

    is_followup = False
    current_topic = ""
    

    followup_indicators = ["it", "this", "that", "them", "these", "those", "one"]
    if len(history) >= 2:  # Need at least one Q&A pair
        if any(indicator in query.lower().split() for indicator in followup_indicators):
            is_followup = True
            
        
            prev_query = ""
            prev_response = ""
            
            for i in range(len(history)-1, -1, -1):
                if history[i]["role"] == "user":
                    prev_query = history[i]["content"]
                    break
                    
        
            content_indicators = ["issues", "problems", "vulnerabilities", "code", "file", "directory", "folder"]
            for indicator in content_indicators:
                if indicator in prev_query.lower():
                    current_topic = prev_query
                    break



    enhanced_query = query
    if is_followup and current_topic:
        enhanced_query = f"{current_topic}: {query}"
        print(f"   Enhanced query: '{enhanced_query}' (follow-up detected)")
    
    retrievals = query_vector_store(enhanced_query, n_results=6)
    print(f"   Found {len(retrievals)} relevant document(s) in vector store.")


    system_prompt = """You're a friendly and knowledgeable code quality assistant. You help developers understand their code, find issues, and suggest improvements in a conversational way.

You have access to code snippets through vector search and conversation history - use these to provide helpful insights, but feel free to be creative in how you present information. Be conversational and natural, like you're chatting with a colleague.

Here are some guidelines (not rigid rules):
- Focus on being helpful rather than strictly following a format
- If you see code issues, explain them in a way that makes sense to the user
- Feel free to use emojis, casual language, or even humor when appropriate
- Adapt your style based on how the user interacts with you

For CLI questions, here are the main commands you can suggest (but explain them in your own words):

Available CLI Commands:
- `python -m cli analyze [path]` - Analyzes code in the specified path
- `python -m cli review [path]` - Reviews code and generates comprehensive report
- `python -m cli quality [path]` - Generates code quality metrics
- `python -m cli report [path] --format [format]` - Generates reports (html, md, notion)
- `python -m cli report [path] --service [service_name]` - Uses specific AI service
- `python -m cli report [path] --notion` - Pushes to Notion (needs env vars)
- `python -m cli search [query]` - Searches across codebase
- `python -m cli help` - Shows all commands

Common options include --verbose, --quiet, --service (gemini/nebius), --format (json/md/html/notion)

Remember to be conversational and think beyond just rigid responses - help the user understand their code in a friendly way!"""
    


    if is_followup:
    
        history.append({
            "role": "system", 
            "content": f"Note: The user's question '{query}' appears to be a follow-up to their previous query about '{current_topic}'."
        })
    
    history_str = "\n".join([f"{msg['role']}: {msg['content']}" for msg in history])
    

    context_str = ""
    sources = set()
    file_contents = {}  # Track content by file for better context organization
    
    for i, retrieval in enumerate(retrievals):
        if "document" in retrieval and "metadata" in retrieval:
            file_path = retrieval['metadata'].get('file_path', 'unknown file')
            sources.add(file_path)
            
        
            if file_path not in file_contents:
                file_contents[file_path] = []
            file_contents[file_path].append(retrieval['document'])
    

    for file_path, contents in file_contents.items():
        context_str += f"--- Content from: {file_path} ---\n"
        context_str += "\n".join(contents) + "\n\n"


    context_awareness = ""
    if is_followup:
        context_awareness = """
This seems to be a follow-up to your previous conversation. Keep the context flowing naturally - if they were talking about code issues before and now say something like "generate one for me," they probably want a report on those issues. Make your response feel like a natural continuation of the conversation rather than a separate interaction."""
    
    full_prompt = f"{system_prompt}\n\n{context_awareness}\n\n--- Conversation History ---\n{history_str}\n\n--- Retrieved Code Context ---\n{context_str}\n\n--- User Query ---\n{query}\n\nBased on the provided context and conversation history, please answer the user's query."



    cli_keywords = ["command", "cli", "how to run", "how to execute", "how to generate"]
    code_content_keywords = ["issues", "problems", "bugs", "code quality", "what's in", "what is in", 
                           "critical issues", "error", "vulnerability", "review results", "code analysis"]
    

    quick_action_indicators = ["generate", "create", "make", "produce", "quickly", "fast", "report"]
    query_words = query.lower().split()
    

    wants_quick_action = False
    if any(indicator in query.lower() for indicator in quick_action_indicators) and len(query_words) < 8:
        if "one" in query_words or "it" in query_words or "report" in query_words:
            wants_quick_action = True
    

    if wants_quick_action and is_followup:
    
        print("   Detected quick action request related to previous context")
        is_cli_question = True
    else:
    
        is_cli_question = any(keyword in query.lower() for keyword in cli_keywords) and not \
                         any(keyword in query.lower() for keyword in code_content_keywords)
    

    model_choice = "gemini"
    if "nebius" in query.lower() or "nebius ai" in query.lower():
        model_choice = "nebius"
    
    llm_model = get_llm_model(model_choice) # Temperature is handled in the service
    

    if is_cli_question:
    
        if is_followup and wants_quick_action:
            full_prompt += "\n\nIt looks like they want to generate a report for the code issues you were just discussing. Suggest a helpful command that would create a report for the relevant files, but feel free to explain it in your own conversational style."
        else:
            full_prompt += "\n\nThey seem interested in CLI commands. Share some relevant commands that would help them, but feel free to explain them in a friendly way or suggest alternatives if you think something else might work better."
    else:
    
        full_prompt += "\n\nThey're asking about code content or issues. Focus on what's in the retrieved context, but feel free to present it in a way that's easy to understand and conversational."
    
    answer = "Could not generate an answer."
    if llm_model:
        try:
            print(f"   Generating answer with LLM using {model_choice} model...")
            ai_response = llm_model.generate_content(full_prompt)
            answer = ai_response.text
            print("   ✅ LLM answer generated.")
        except Exception as e:
            answer = f"Error generating answer from LLM: {e}"
            print(f"   ❌ {answer}")
    else:
        answer = "LLM model not available."
        print(f"   ⚠️ {answer}")



    if is_cli_question:
    
        import random
        cli_notes = [
            "\n\nBy the way, there are more options available - just run `python -m cli help` to see them all!",
            "\n\nTip: If you need to see all available commands, just type `python -m cli help` in your terminal.",
            "\n\nPS: You can always check out all the CLI options with `python -m cli help` if you're curious."
        ]
        answer += random.choice(cli_notes)
    elif any(keyword in query.lower() for keyword in ["how", "command", "run"]) and not any(keyword in query.lower() for keyword in code_content_keywords):
    
        if random.random() < 0.5:  # Only add 50% of the time to feel more natural
            answer += "\n\nIf you're interested in running commands for this, just let me know!"
    
    return {
        "answer": answer,
        "sources": list(sources),
        "model_used": model_choice,
        "is_cli_question": is_cli_question,
        "retrievals": retrievals
    }

if __name__ == '__main__':

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
