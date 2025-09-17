'use client'

import { useState, useEffect } from 'react'
import { CheckCircle, Clock, AlertTriangle, Loader, RefreshCw } from 'lucide-react'
import { apiService, AnalysisStatus } from '../utils/apiService'

interface JobStatusProps {
  jobId: string
  onComplete: (results: AnalysisStatus) => void
  onError: (error: string) => void
}

export default function JobStatus({ jobId, onComplete, onError }: JobStatusProps) {
  const [status, setStatus] = useState<AnalysisStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    let intervalId: NodeJS.Timeout

    const pollStatus = async () => {
      try {
        const statusData = await apiService.getAnalysisStatus(jobId)
        setStatus(statusData)
        setError(null)

        if (statusData.status === 'completed') {
          onComplete(statusData)
          clearInterval(intervalId)
        } else if (statusData.status === 'failed') {
          onError(statusData.message || 'Analysis failed')
          clearInterval(intervalId)
        }
      } catch (err: any) {
        setError(err.message || 'Failed to check status')
        onError(err.message || 'Failed to check status')
      } finally {
        setLoading(false)
      }
    }

    // Initial poll
    pollStatus()

    // Set up polling every 3 seconds
    intervalId = setInterval(pollStatus, 3000)

    return () => {
      if (intervalId) clearInterval(intervalId)
    }
  }, [jobId, onComplete, onError])

  const getStatusIcon = () => {
    switch (status?.status) {
      case 'pending':
        return <Clock className="h-6 w-6 text-yellow-400" />
      case 'processing':
        return <Loader className="h-6 w-6 text-blue-400 animate-spin" />
      case 'completed':
        return <CheckCircle className="h-6 w-6 text-green-400" />
      case 'failed':
        return <AlertTriangle className="h-6 w-6 text-red-400" />
      default:
        return <RefreshCw className="h-6 w-6 text-gray-400" />
    }
  }

  const getStatusColor = () => {
    switch (status?.status) {
      case 'pending':
        return 'text-yellow-400'
      case 'processing':
        return 'text-blue-400'
      case 'completed':
        return 'text-green-400'
      case 'failed':
        return 'text-red-400'
      default:
        return 'text-gray-400'
    }
  }

  const getStatusMessage = () => {
    switch (status?.status) {
      case 'pending':
        return 'Analysis queued and waiting to start...'
      case 'processing':
        return 'Analyzing your code for quality issues...'
      case 'completed':
        return 'Analysis completed successfully!'
      case 'failed':
        return status?.message || 'Analysis failed'
      default:
        return 'Checking analysis status...'
    }
  }

  if (loading && !status) {
    return (
      <div className="glass rounded-xl p-8 text-center">
        <Loader className="h-16 w-16 text-neon-blue mx-auto mb-4 animate-spin" />
        <h3 className="text-2xl font-semibold mb-2">Initializing Analysis</h3>
        <p className="text-gray-400">Setting up your analysis job...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass rounded-xl p-8 text-center">
        <AlertTriangle className="h-16 w-16 text-red-400 mx-auto mb-4" />
        <h3 className="text-2xl font-semibold mb-2">Analysis Error</h3>
        <p className="text-gray-400 mb-4">{error}</p>
        <button
          onClick={() => window.location.reload()}
          className="bg-gradient-to-r from-neon-blue to-neon-purple text-white px-6 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300"
        >
          Try Again
        </button>
      </div>
    )
  }

  return (
    <div className="glass rounded-xl p-8">
      <div className="text-center mb-6">
        {getStatusIcon()}
        <h3 className="text-2xl font-semibold mt-4 mb-2">Analysis in Progress</h3>
        <p className={`text-lg ${getStatusColor()}`}>
          {getStatusMessage()}
        </p>
      </div>

      {/* Progress Information */}
      {status?.status === 'processing' && (
        <div className="space-y-4">
          <div className="bg-dark-surface rounded-lg p-4">
            <div className="flex justify-between items-center mb-2">
              <span className="text-gray-300">Progress</span>
              <span className="text-white font-semibold">
                {status.progress || 0}%
              </span>
            </div>
            <div className="w-full bg-gray-700 rounded-full h-2">
              <div
                className="bg-gradient-to-r from-neon-blue to-neon-purple h-2 rounded-full transition-all duration-500"
                style={{ width: `${status.progress || 0}%` }}
              />
            </div>
          </div>

          {status.message && (
            <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-4">
              <p className="text-blue-200 text-sm">{status.message}</p>
            </div>
          )}
        </div>
      )}

      {/* Job Information */}
      <div className="mt-6 pt-6 border-t border-white/10">
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-gray-400">Job ID:</span>
            <p className="text-white font-mono">{jobId.slice(0, 8)}...</p>
          </div>
          <div>
            <span className="text-gray-400">Status:</span>
            <p className={`font-semibold capitalize ${getStatusColor()}`}>
              {status?.status}
            </p>
          </div>
        </div>
      </div>

      {/* Estimated Time */}
      {status?.status === 'processing' && (
        <div className="mt-4 text-center">
          <p className="text-gray-400 text-sm">
            This usually takes 1-3 minutes depending on repository size
          </p>
        </div>
      )}
    </div>
  )
}