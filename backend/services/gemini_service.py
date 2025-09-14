import os
from typing import Dict, Any, Optional
import google.generativeai as genai
from dotenv import load_dotenv

from ..models.analysis_models import ChatResponse

load_dotenv()

class GeminiService:
    def __init__(self):
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
        self.chat_history = []
    
    async def chat(self, message: str, context: Optional[Dict[str, Any]] = None) -> ChatResponse:
        """Chat about the codebase using Gemini"""
        
        # Build context-aware prompt
        system_prompt = """You are a code quality expert assistant. You help developers understand their codebase, 
        explain code quality issues, and provide actionable suggestions for improvement.
        
        When discussing code issues:
        - Be specific and actionable
        - Explain the impact of issues
        - Provide concrete examples when possible
        - Prioritize security and performance concerns
        - Use developer-friendly language
        """
        
        # Add context if available
        context_info = ""
        if context:
            if 'analysis_result' in context:
                result = context['analysis_result']
                context_info = f"""
                
                Current codebase analysis context:
                - Total files: {result.get('total_files', 0)}
                - Total issues: {result.get('summary', {}).get('total_issues', 0)}
                - Languages: {', '.join(result.get('summary', {}).get('languages_detected', []))}
                - Average complexity: {result.get('summary', {}).get('average_complexity', 0)}
                """
        
        full_prompt = f"{system_prompt}{context_info}\n\nUser question: {message}"
        
        try:
            response = self.model.generate_content(full_prompt)
            
            # Store in chat history
            self.chat_history.append({"role": "user", "content": message})
            self.chat_history.append({"role": "assistant", "content": response.text})
            
            # Generate suggestions based on the conversation
            suggestions = self._generate_suggestions(message, response.text)
            
            return ChatResponse(
                message=response.text,
                context_used=context is not None,
                suggestions=suggestions
            )
            
        except Exception as e:
            return ChatResponse(
                message=f"I apologize, but I encountered an error: {str(e)}",
                context_used=False,
                suggestions=["Try rephrasing your question", "Check your API key configuration"]
            ) 
   
    def _generate_suggestions(self, user_message: str, ai_response: str) -> list[str]:
        """Generate follow-up suggestions based on the conversation"""
        suggestions = []
        
        # Common follow-up questions based on message content
        if "security" in user_message.lower():
            suggestions.extend([
                "What are the most critical security issues?",
                "How can I implement security best practices?",
                "Show me examples of secure coding patterns"
            ])
        elif "performance" in user_message.lower():
            suggestions.extend([
                "What are the biggest performance bottlenecks?",
                "How can I optimize this code?",
                "What performance monitoring should I add?"
            ])
        elif "complexity" in user_message.lower():
            suggestions.extend([
                "Which functions are too complex?",
                "How can I reduce cyclomatic complexity?",
                "What refactoring patterns should I use?"
            ])
        else:
            suggestions.extend([
                "What are the top priority issues to fix?",
                "How can I improve code maintainability?",
                "What testing strategy do you recommend?"
            ])
        
        return suggestions[:3]  # Limit to 3 suggestions
    
    def clear_history(self):
        """Clear chat history"""
        self.chat_history = []
    
    def get_history(self):
        """Get chat history"""
        return self.chat_history
