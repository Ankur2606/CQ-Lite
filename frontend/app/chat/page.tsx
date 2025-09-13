'use client'

import { useState, useRef, useEffect } from 'react'
import { Send, Code, Bot, User, Lightbulb } from 'lucide-react'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp: string
  suggestions?: string[]
}

export default function Chat() {
  const [messages, setMessages] = useState<Message[]>([
    {
      role: 'assistant',
      content: 'Hello! I\'m your Code Quality AI assistant. I can help you understand your codebase, explain issues, and provide suggestions for improvement. What would you like to know?',
      timestamp: '2024-01-01T00:00:00.000Z',
      suggestions: [
        'What are the most critical issues in my code?',
        'How can I improve code maintainability?',
        'Show me security vulnerabilities'
      ]
    }
  ])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [isClient, setIsClient] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    setIsClient(true)
  }, [])

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (message: string) => {
    if (!message.trim() || isLoading) return

    const userMessage: Message = {
      role: 'user',
      content: message,
      timestamp: new Date().toISOString()
    }

    setMessages(prev => [...prev, userMessage])
    setInputMessage('')
    setIsLoading(true)

    try {
      // Simulate API call
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      const assistantMessage: Message = {
        role: 'assistant',
        content: `I understand you're asking about: "${message}". Based on your codebase analysis, here are some insights:\n\n• This appears to be related to code quality concerns\n• I recommend focusing on the highest impact issues first\n• Consider implementing automated testing for better coverage\n\nWould you like me to elaborate on any specific aspect?`,
        timestamp: new Date().toISOString(),
        suggestions: [
          'Tell me more about security issues',
          'How do I reduce complexity?',
          'What testing strategy do you recommend?'
        ]
      }

      setMessages(prev => [...prev, assistantMessage])
    } catch (error) {
      console.error('Error sending message:', error)
    } finally {
      setIsLoading(false)
    }
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault()
    sendMessage(inputMessage)
  }

  const handleSuggestionClick = (suggestion: string) => {
    sendMessage(suggestion)
  }

  return (
    <div className="min-h-screen bg-cyber-gradient flex flex-col">
      {/* Navigation */}
      <nav className="glass border-b border-white/10 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Code className="h-8 w-8 text-neon-blue" />
            <span className="text-xl font-bold gradient-text">CodeQuality AI</span>
          </div>
          <div className="flex space-x-6">
            <a href="/dashboard" className="text-gray-300 hover:text-white transition-colors">
              Dashboard
            </a>
            <span className="text-white font-semibold">Chat</span>
          </div>
        </div>
      </nav>

      {/* Chat Container */}
      <div className="flex-1 max-w-4xl mx-auto w-full px-4 py-8 flex flex-col">
        <div className="glass rounded-2xl flex-1 flex flex-col overflow-hidden">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-6 space-y-6">
            {messages.map((message, index) => (
              <div key={index} className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}>
                <div className={`flex max-w-3xl ${message.role === 'user' ? 'flex-row-reverse' : 'flex-row'} space-x-3`}>
                  {/* Avatar */}
                  <div className={`flex-shrink-0 w-10 h-10 rounded-full flex items-center justify-center ${
                    message.role === 'user' 
                      ? 'bg-gradient-to-r from-neon-blue to-neon-purple' 
                      : 'bg-gradient-to-r from-purple-500 to-pink-500'
                  }`}>
                    {message.role === 'user' ? (
                      <User className="h-5 w-5 text-white" />
                    ) : (
                      <Bot className="h-5 w-5 text-white" />
                    )}
                  </div>

                  {/* Message Content */}
                  <div className={`flex-1 ${message.role === 'user' ? 'mr-3' : 'ml-3'}`}>
                    <div className={`p-4 rounded-2xl ${
                      message.role === 'user'
                        ? 'bg-gradient-to-r from-neon-blue to-neon-purple text-white'
                        : 'bg-white/10 text-gray-100 border border-white/20'
                    }`}>
                      <p className="whitespace-pre-wrap">{message.content}</p>
                    </div>

                    {/* Suggestions */}
                    {message.suggestions && message.role === 'assistant' && (
                      <div className="mt-3 space-y-2">
                        <div className="flex items-center space-x-2 text-sm text-gray-400">
                          <Lightbulb className="h-4 w-4" />
                          <span>Suggestions:</span>
                        </div>
                        <div className="space-y-2">
                          {message.suggestions.map((suggestion, idx) => (
                            <button
                              key={idx}
                              onClick={() => handleSuggestionClick(suggestion)}
                              className="block w-full text-left p-3 bg-white/5 hover:bg-white/10 rounded-lg border border-white/10 text-sm text-gray-300 hover:text-white transition-all"
                            >
                              {suggestion}
                            </button>
                          ))}
                        </div>
                      </div>
                    )}

                    <div className="mt-2 text-xs text-gray-500">
                      {isClient ? new Date(message.timestamp).toLocaleTimeString() : ''}
                    </div>
                  </div>
                </div>
              </div>
            ))}

            {isLoading && (
              <div className="flex justify-start">
                <div className="flex space-x-3">
                  <div className="w-10 h-10 rounded-full bg-gradient-to-r from-purple-500 to-pink-500 flex items-center justify-center">
                    <Bot className="h-5 w-5 text-white" />
                  </div>
                  <div className="bg-white/10 border border-white/20 rounded-2xl p-4">
                    <div className="flex space-x-2">
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                      <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                    </div>
                  </div>
                </div>
              </div>
            )}

            <div ref={messagesEndRef} />
          </div>

          {/* Input Form */}
          <div className="border-t border-white/10 p-6">
            <form onSubmit={handleSubmit} className="flex space-x-4">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                placeholder="Ask me about your code quality..."
                className="flex-1 bg-white/10 border border-white/20 rounded-xl px-4 py-3 text-white placeholder-gray-400 focus:outline-none focus:ring-2 focus:ring-neon-blue focus:border-transparent"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!inputMessage.trim() || isLoading}
                className="bg-gradient-to-r from-neon-blue to-neon-purple text-white p-3 rounded-xl hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="h-5 w-5" />
              </button>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}