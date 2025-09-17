'use client'

import { useState } from 'react'
import { Github, Zap, Brain, FileText, Settings, Play } from 'lucide-react'
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

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!repoUrl.trim()) {
      onError('Please enter a GitHub repository URL')
      return
    }

    setIsLoading(true)
    try {
      const request: GitHubAnalysisRequest = {
        repo_url: repoUrl.trim(),
        service,
        max_files: maxFiles,
        include_patterns: includePatterns
      }

      const response = await apiService.analyzeGitHubRepo(request)
      onAnalysisStart(response.job_id)
    } catch (error: any) {
      onError(error.response?.data?.detail || 'Failed to start analysis')
    } finally {
      setIsLoading(false)
    }
  }

  const togglePattern = (pattern: string) => {
    setIncludePatterns(prev =>
      prev.includes(pattern)
        ? prev.filter(p => p !== pattern)
        : [...prev, pattern]
    )
  }

  return (
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
              className={`p-4 rounded-lg border-2 transition-all ${
                service === 'nebius'
                  ? 'border-neon-blue bg-neon-blue/10'
                  : 'border-white/20 bg-dark-surface hover:border-white/40'
              }`}
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
              className={`p-4 rounded-lg border-2 transition-all ${
                service === 'gemini'
                  ? 'border-neon-blue bg-neon-blue/10'
                  : 'border-white/20 bg-dark-surface hover:border-white/40'
              }`}
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
                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${
                  includePatterns.includes(pattern)
                    ? 'bg-neon-blue text-white'
                    : 'bg-white/10 text-gray-300 hover:bg-white/20'
                }`}
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
              className="w-20 px-3 py-2 bg-dark-surface border border-white/20 rounded text-white text-center focus:border-neon-blue focus:outline-none"
            />
          </div>
        </div>

        {/* Submit Button */}
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-neon-blue to-neon-purple text-white py-4 px-6 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Starting Analysis...</span>
            </>
          ) : (
            <>
              <Play className="h-5 w-5" />
              <span>Start Analysis</span>
            </>
          )}
        </button>
      </form>
    </div>
  )
}