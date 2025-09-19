'use client'

import { useState, useEffect } from 'react'
import { Github, Zap, Brain, FileText, Settings, Play, RefreshCw } from 'lucide-react'
import { apiService, GitHubAnalysisRequest } from '../utils/apiService'

interface GitHubAnalysisFormProps {
  onAnalysisStart: (jobId: string) => void;
  onError: (error: string) => void;
}

export default function GitHubAnalysisForm({ onAnalysisStart, onError }: GitHubAnalysisFormProps) {
  const [repoUrl, setRepoUrl] = useState('')
  const [service, setService] = useState<'gemini' | 'nebius'>('nebius')
  const [maxFiles, setMaxFiles] = useState(12)
  const [includePatterns, setIncludePatterns] = useState(['*.py', '*.js', '*.ts', '*.jsx', '*.tsx'])
  const [isLoading, setIsLoading] = useState(false)
  const [showWakeUpMessage, setShowWakeUpMessage] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  const [errorToast, setErrorToast] = useState<string | null>(null)

  const MAX_RETRIES = 3
  const RETRY_INTERVAL = 15000 // 15 seconds
  const REQUEST_TIMEOUT = 60000 // 60 seconds

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!repoUrl.trim()) {
      onError('Please enter a GitHub repository URL')
      return
    }

    setIsLoading(true)
    setShowWakeUpMessage(false)
    setRetryCount(0)
    setErrorToast(null)

    const request: GitHubAnalysisRequest = {
      repo_url: repoUrl.trim(),
      service,
      max_files: maxFiles,
      include_patterns: includePatterns
    }

    await attemptAnalysis(request)
  }

  const attemptAnalysis = async (request: GitHubAnalysisRequest, isRetry = false) => {
    try {
      // Create axios instance with longer timeout for wake-up handling
      const axiosInstance = apiService['axiosInstance'] || (await import('axios')).default.create({
        baseURL: process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000',
        timeout: REQUEST_TIMEOUT,
      })

      const response = await axiosInstance.post('/api/analyze/github', request)
      const data = response.data

      // Success! Redirect to dashboard
      setIsLoading(false)
      setShowWakeUpMessage(false)
      onAnalysisStart(data.job_id)

    } catch (error: any) {
      const newRetryCount = retryCount + 1
      setRetryCount(newRetryCount)

      if (newRetryCount < MAX_RETRIES) {
        // Show wake-up message on first timeout
        if (!isRetry) {
          setShowWakeUpMessage(true)
        }

        // Retry after interval
        setTimeout(() => {
          attemptAnalysis(request, true)
        }, RETRY_INTERVAL)
      } else {
        // All retries failed
        setIsLoading(false)
        setShowWakeUpMessage(false)
        setErrorToast('Hmm, still sleepy. Try refreshing the page and starting again.')
      }
    }
  }

  const handleRetry = () => {
    setErrorToast(null)
    setIsLoading(false)
    setShowWakeUpMessage(false)
    setRetryCount(0)
  }

  // Clear error toast after 5 seconds
  useEffect(() => {
    if (errorToast) {
      const timer = setTimeout(() => setErrorToast(null), 5000)
      return () => clearTimeout(timer)
    }
  }, [errorToast])

  const togglePattern = (pattern: string) => {
    setIncludePatterns(prev =>
      prev.includes(pattern)
        ? prev.filter(p => p !== pattern)
        : [...prev, pattern]
    )
  }

  return (
    <div className="relative">
      {/* Persistent Loading Overlay */}
      {isLoading && (
        <div className="fixed inset-0 bg-black/20 backdrop-blur-sm z-50 flex items-center justify-center">
          <div className="text-center">
            {/* Orbital Loading Animation */}
            <div className="relative w-20 h-20 mx-auto mb-6">
              <div className="absolute inset-0 rounded-full border-4 border-transparent border-t-blue-400 border-r-blue-300 animate-spin"></div>
              <div className="absolute inset-2 rounded-full border-4 border-transparent border-t-blue-300 border-r-blue-200 animate-spin animation-delay-150"></div>
              <div className="absolute inset-4 rounded-full border-4 border-transparent border-t-blue-200 animate-spin animation-delay-300"></div>
            </div>
            <p className="text-white text-lg font-medium">Starting Analysis...</p>
          </div>
        </div>
      )}

      {/* Wake-up Message Overlay */}
      {showWakeUpMessage && (
        <div className="fixed bottom-6 left-1/2 transform -translate-x-1/2 z-[100] wake-up-message">
          <div className="bg-gradient-to-r from-blue-900/95 to-slate-900/95 border border-blue-500/30 rounded-xl p-6 shadow-2xl max-w-md">
            <div className="text-center">
              <div className="text-4xl mb-3 animate-pulse">😊</div>
              <p className="text-blue-100 text-base leading-relaxed gentle-pulse">
                The backend is hosted on Render and may take a moment to wake up. 
                <span className="italic font-medium">Thank you for your patience!</span>
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Error Toast */}
      {errorToast && (
        <div className="fixed top-6 right-6 z-50">
          <div className="bg-red-900/90 backdrop-blur-md border border-red-500/30 rounded-lg p-4 shadow-2xl max-w-sm">
            <div className="flex items-center justify-between">
              <p className="text-red-100 text-sm">{errorToast}</p>
              <button
                onClick={handleRetry}
                className="ml-4 bg-red-700 hover:bg-red-600 text-white px-3 py-1 rounded text-sm font-medium transition-colors flex items-center gap-1"
              >
                <RefreshCw className="h-3 w-3" />
                Retry
              </button>
            </div>
          </div>
        </div>
      )}

      <div className="glass rounded-2xl p-8">
        <div className="flex items-center space-x-3 mb-6">
          <Github className="h-8 w-8 text-white" />
          <h2 className="text-2xl font-bold gradient-text">GitHub Repository Analysis</h2>
        </div>

        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Repository URL */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-2">
              GitHub Repository URL
            </label>
            <input
              type="url"
              value={repoUrl}
              onChange={(e) => setRepoUrl(e.target.value)}
              placeholder="https://github.com/username/repository"
              className="w-full px-4 py-3 bg-dark-surface border border-white/20 rounded-lg text-white placeholder-gray-500 focus:border-neon-blue focus:outline-none transition-colors"
              required
              disabled={isLoading}
            />
          </div>

          {/* AI Service Selection */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              AI Analysis Service
            </label>
            <div className="grid grid-cols-2 gap-3">
              <button
                type="button"
                onClick={() => setService('nebius')}
                disabled={isLoading}
                className={`p-4 rounded-lg border-2 transition-all ${
                  service === 'nebius'
                    ? 'border-neon-blue bg-neon-blue/10'
                    : 'border-white/20 bg-dark-surface hover:border-white/40'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="flex items-center space-x-3">
                  <Zap className="h-6 w-6 text-yellow-400" />
                  <div className="text-left">
                    <div className="font-semibold text-white">Nebius</div>
                    <div className="text-sm text-gray-400">Fast & Efficient</div>
                  </div>
                </div>
              </button>

              <button
                type="button"
                onClick={() => setService('gemini')}
                disabled={isLoading}
                className={`p-4 rounded-lg border-2 transition-all ${
                  service === 'gemini'
                    ? 'border-neon-blue bg-neon-blue/10'
                    : 'border-white/20 bg-dark-surface hover:border-white/40'
                } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
              >
                <div className="flex items-center space-x-3">
                  <Brain className="h-6 w-6 text-purple-400" />
                  <div className="text-left">
                    <div className="font-semibold text-white">Gemini</div>
                    <div className="text-sm text-gray-400">Advanced Analysis</div>
                  </div>
                </div>
              </button>
            </div>
          </div>

          {/* File Patterns */}
          <div>
            <label className="block text-sm font-medium text-gray-300 mb-3">
              File Types to Analyze
            </label>
            <div className="flex flex-wrap gap-2">
              {['*.py', '*.js', '*.ts', '*.jsx', '*.tsx', '*.java', '*.cpp', '*.go'].map(pattern => (
                <button
                  key={pattern}
                  type="button"
                  onClick={() => togglePattern(pattern)}
                  disabled={isLoading}
                  className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                    includePatterns.includes(pattern)
                      ? 'bg-neon-blue text-white'
                      : 'bg-white/10 text-gray-300 hover:bg-white/20'
                  } ${isLoading ? 'opacity-50 cursor-not-allowed' : ''}`}
                >
                  {pattern}
                </button>
              ))}
            </div>
          </div>

          {/* Advanced Options */}
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div>
                <label className="text-sm font-medium text-gray-300">Max Files</label>
                <p className="text-xs text-gray-500">Maximum 12 files to analyze</p>
              </div>
              <input
                type="number"
                value={maxFiles}
                onChange={(e) => setMaxFiles(Number(e.target.value))}
                min="1"
                max="12"
                disabled={isLoading}
                className="w-20 px-3 py-2 bg-dark-surface border border-white/20 rounded text-white text-center focus:border-neon-blue focus:outline-none disabled:opacity-50"
              />
            </div>
          </div>

          {/* Submit Button */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-gradient-to-r from-blue-600 to-purple-600 hover:from-blue-500 hover:to-purple-500 text-white py-4 px-8 rounded-xl font-semibold shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed disabled:transform-none flex items-center justify-center space-x-3 text-lg"
            aria-label={isLoading ? "Analysis in progress" : "Start Analysis"}
          >
            {isLoading ? (
              <>
                <div className="animate-spin rounded-full h-6 w-6 border-b-2 border-white"></div>
                <span>Starting Analysis...</span>
              </>
            ) : (
              <>
                <Play className="h-6 w-6" />
                <span>Start Analysis</span>
              </>
            )}
          </button>
        </form>
      </div>
    </div>
  )
}