'use client'

import { useState, useRef, useEffect } from 'react'
import { Upload, FileText, X, CheckCircle, RefreshCw } from 'lucide-react'
import { apiService } from '../utils/apiService'

interface FileUploadFormProps {
  onAnalysisStart: (jobId: string) => void;
  onError: (error: string) => void;
}

export default function FileUploadForm({ onAnalysisStart, onError }: FileUploadFormProps) {
  const [dragActive, setDragActive] = useState(false)
  const [selectedFiles, setSelectedFiles] = useState<File[]>([])
  const [isLoading, setIsLoading] = useState(false)
  const [maxFiles, setMaxFiles] = useState(12)
  const [showWakeUpMessage, setShowWakeUpMessage] = useState(false)
  const [retryCount, setRetryCount] = useState(0)
  const [errorToast, setErrorToast] = useState<string | null>(null)
  const fileInputRef = useRef<HTMLInputElement>(null)

  const MAX_RETRIES = 3
  const RETRY_INTERVAL = 15000 // 15 seconds
  const REQUEST_TIMEOUT = 60000 // 60 seconds

  const handleDrag = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true)
    } else if (e.type === "dragleave") {
      setDragActive(false)
    }
  }

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault()
    e.stopPropagation()
    setDragActive(false)

    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFiles(e.dataTransfer.files)
    }
  }

  const handleFiles = (files: FileList) => {
    const fileArray = Array.from(files)
    
    // Check if adding these files would exceed the limit
    if (selectedFiles.length + fileArray.length > maxFiles) {
      onError(`Maximum ${maxFiles} files allowed. You currently have ${selectedFiles.length} files selected.`)
      return
    }
    
    setSelectedFiles(prev => [...prev, ...fileArray])
  }

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleFiles(e.target.files)
    }
  }

  const removeFile = (index: number) => {
    setSelectedFiles(prev => prev.filter((_, i) => i !== index))
  }

  const handleSubmit = async () => {
    if (selectedFiles.length === 0) {
      onError('Please select at least one file')
      return
    }

    setIsLoading(true)
    setShowWakeUpMessage(false)
    setRetryCount(0)
    setErrorToast(null)

    await attemptAnalysis()
  }

  const attemptAnalysis = async (isRetry = false) => {
    try {
      const response = await apiService.uploadFiles(selectedFiles, maxFiles)

      // Success! Redirect to dashboard
      setIsLoading(false)
      setShowWakeUpMessage(false)
      onAnalysisStart(response.job_id)

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
          attemptAnalysis(true)
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

  const formatFileSize = (bytes: number) => {
    if (bytes === 0) return '0 Bytes'
    const k = 1024
    const sizes = ['Bytes', 'KB', 'MB', 'GB']
    const i = Math.floor(Math.log(bytes) / Math.log(k))
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
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
        <Upload className="h-8 w-8 text-white" />
        <h2 className="text-2xl font-bold gradient-text">File Upload Analysis</h2>
      </div>

      {/* Settings */}
      <div className="mb-6">
        <label className="block text-sm font-medium text-gray-300 mb-2">
          Maximum Files to Analyze
        </label>
        <input
          type="number"
          min="1"
          max="50"
          value={maxFiles}
          onChange={(e) => setMaxFiles(Number(e.target.value))}
          className="w-32 bg-white/10 border border-white/20 rounded-lg px-3 py-2 text-white focus:outline-none focus:border-neon-blue"
        />
      </div>

      {/* Upload Area */}
      <div
        className={`border-2 border-dashed rounded-xl p-8 text-center transition-all duration-300 mb-6 ${
          selectedFiles.length >= maxFiles
            ? 'border-gray-600 bg-gray-800/50 cursor-not-allowed'
            : dragActive
            ? 'border-neon-blue bg-neon-blue/10 scale-105'
            : 'border-white/20 bg-dark-surface hover:border-white/40'
        }`}
        onDragEnter={handleDrag}
        onDragLeave={handleDrag}
        onDragOver={handleDrag}
        onDrop={handleDrop}
      >
        <Upload className="h-16 w-16 text-neon-blue mx-auto mb-4" />
        <h3 className="text-xl font-semibold mb-2">Drop your files here</h3>
        <p className="text-gray-400 mb-4">Select up to {maxFiles} files total for analysis</p>
        <button
          type="button"
          onClick={() => fileInputRef.current?.click()}
          disabled={selectedFiles.length >= maxFiles}
          className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 ${
            selectedFiles.length >= maxFiles
              ? 'bg-gray-600 text-gray-400 cursor-not-allowed'
              : 'bg-gradient-to-r from-neon-blue to-neon-purple text-white hover:shadow-lg'
          }`}
        >
          {selectedFiles.length >= maxFiles ? 'File Limit Reached' : 'Choose Files'}
        </button>
        <input
          ref={fileInputRef}
          type="file"
          multiple
          onChange={handleFileSelect}
          disabled={selectedFiles.length >= maxFiles}
          className="hidden"
          accept=".py,.js,.ts,.jsx,.tsx,.java,.cpp,.go,.rb,.php,.cs,.html,.css,.json,.yml,.yaml,.md,.txt"
        />
      </div>

      {/* File Limit Info */}
      <div className="text-center mb-4">
        <p className="text-xs text-gray-500">
          Maximum {maxFiles} files allowed for upload and analysis
        </p>
      </div>

      {/* Selected Files */}
      {selectedFiles.length > 0 && (
        <div className="mb-6">
          <h4 className="text-lg font-semibold mb-4">Selected Files ({selectedFiles.length}/{maxFiles})</h4>
          <div className="space-y-2 max-h-60 overflow-y-auto">
            {selectedFiles.map((file, index) => (
              <div key={index} className="flex items-center justify-between bg-white/5 rounded-lg p-3">
                <div className="flex items-center space-x-3">
                  <FileText className="h-5 w-5 text-neon-blue" />
                  <div>
                    <p className="text-white font-medium truncate max-w-xs">{file.name}</p>
                    <p className="text-gray-400 text-sm">{formatFileSize(file.size)}</p>
                  </div>
                </div>
                <button
                  onClick={() => removeFile(index)}
                  className="text-red-400 hover:text-red-300 transition-colors"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Submit Button */}
      {selectedFiles.length > 0 && (
        <button
          onClick={handleSubmit}
          disabled={isLoading}
          className="w-full bg-gradient-to-r from-neon-blue to-neon-purple text-white py-4 px-6 rounded-lg font-semibold hover:shadow-lg transition-all duration-300 disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center space-x-2"
        >
          {isLoading ? (
            <>
              <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
              <span>Uploading & Analyzing...</span>
            </>
          ) : (
            <>
              <CheckCircle className="h-5 w-5" />
              <span>Analyze Files ({selectedFiles.length})</span>
            </>
          )}
        </button>
      )}
    </div>
    </div>
  )
}