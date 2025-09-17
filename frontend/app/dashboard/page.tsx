'use client'

import { useState, useEffect } from 'react'
import { useSearchParams, useRouter } from 'next/navigation'
import { Code, ArrowLeft } from 'lucide-react'
import { apiService, AnalysisStatus } from '../../utils/apiService'
import JobStatus from '../../components/JobStatus'
import AnalysisResults from '../../components/AnalysisResults'

export default function Dashboard() {
  const searchParams = useSearchParams()
  const router = useRouter()
  const jobId = searchParams.get('jobId')
  const [currentView, setCurrentView] = useState<'status' | 'results'>('status')
  const [analysisResults, setAnalysisResults] = useState<AnalysisStatus | null>(null)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    if (!jobId) {
      // No job ID provided, show initial state
      setCurrentView('status')
    }
  }, [jobId])

  const handleAnalysisComplete = (results: AnalysisStatus) => {
    setAnalysisResults(results)
    setCurrentView('results')
  }

  const handleAnalysisError = (errorMessage: string) => {
    setError(errorMessage)
  }

  const handleNewAnalysis = () => {
    // Navigate to home page for new analysis
    router.push('/')
  }

  if (!jobId) {
    return (
      <div className="min-h-screen bg-cyber-gradient">
        {/* Navigation */}
        <nav className="glass border-b border-white/10 p-4">
          <div className="max-w-7xl mx-auto flex items-center justify-between">
            <div className="flex items-center space-x-2">
              <Code className="h-8 w-8 text-neon-blue" />
              <span className="text-xl font-bold gradient-text">CodeQuality AI</span>
            </div>
            <div className="flex space-x-6">
              <a href="/" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2">
                <ArrowLeft className="h-4 w-4" />
                Home
              </a>
            </div>
          </div>
        </nav>

        <div className="max-w-7xl mx-auto px-4 py-8">
          <div className="glass rounded-2xl p-8 text-center">
            <Code className="h-16 w-16 text-neon-blue mx-auto mb-6" />
            <h3 className="text-2xl font-semibold mb-4">No Analysis Job</h3>
            <p className="text-gray-400 mb-6">
              Start a new analysis from the home page to see results here
            </p>
            <a
              href="/"
              className="bg-gradient-to-r from-neon-blue to-neon-purple text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 inline-block"
            >
              Start Analysis
            </a>
          </div>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-cyber-gradient">
      {/* Navigation */}
      <nav className="glass border-b border-white/10 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Code className="h-8 w-8 text-neon-blue" />
            <span className="text-xl font-bold gradient-text">CodeQuality AI</span>
          </div>
          <div className="flex space-x-6">
            <a href="/" className="text-gray-300 hover:text-white transition-colors flex items-center gap-2">
              <ArrowLeft className="h-4 w-4" />
              Home
            </a>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-4">
            {currentView === 'status' ? 'Analysis in Progress' : 'Analysis Results'}
          </h1>
          <p className="text-gray-300">
            {currentView === 'status'
              ? 'Your code is being analyzed for quality issues'
              : 'Review your code analysis results and recommendations'
            }
          </p>
        </div>

        {/* Error State */}
        {error && (
          <div className="glass rounded-xl p-6 mb-6">
            <div className="flex items-center gap-3 text-red-400">
              <div className="text-red-400 font-semibold">Analysis Error:</div>
              <div>{error}</div>
            </div>
            <button
              onClick={handleNewAnalysis}
              className="mt-4 bg-gradient-to-r from-neon-blue to-neon-purple text-white px-6 py-2 rounded-lg font-semibold hover:shadow-lg transition-all duration-300"
            >
              Try New Analysis
            </button>
          </div>
        )}

        {/* Content */}
        {currentView === 'status' && !error && (
          <JobStatus
            jobId={jobId}
            onComplete={handleAnalysisComplete}
            onError={handleAnalysisError}
          />
        )}

        {currentView === 'results' && analysisResults && (
          <AnalysisResults
            results={analysisResults}
            onNewAnalysis={handleNewAnalysis}
          />
        )}
      </div>
    </div>
  )
}