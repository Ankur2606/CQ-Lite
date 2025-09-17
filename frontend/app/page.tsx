'use client'

import { useState } from 'react'
import { Code, Github, Upload, MessageCircle, Zap, Shield, Target } from 'lucide-react'
import Link from 'next/link'
import GitHubAnalysisForm from '../components/GitHubAnalysisForm'
import FileUploadForm from '../components/FileUploadForm'

export default function Home() {
  const [activeTab, setActiveTab] = useState<'github' | 'upload'>('github')

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="glass border-b border-white/10 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Code className="h-8 w-8 text-neon-blue" />
            <span className="text-xl font-bold gradient-text">CQ Lite</span>
          </div>
          <div className="flex space-x-6">
            <Link href="/dashboard" className="text-gray-300 hover:text-white transition-colors">
              Dashboard
            </Link>
            <Link href="/chat" className="text-gray-300 hover:text-white transition-colors">
              Chat
            </Link>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 py-20">
        <div className="text-center mb-16">
          <h1 className="text-6xl font-bold mb-6">
            <span className="gradient-text">AI-Powered</span>
            <br />
            CQ Lite
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
            Analyze your codebase with advanced AST-based analytics, detect security vulnerabilities,
            performance issues, and get AI-powered insights to improve your code quality.
          </p>
        </div>

        {/* Analysis Options */}
        <div className="max-w-6xl mx-auto mb-16">
          {/* Tab Navigation */}
          <div className="flex justify-center mb-8">
            <div className="glass rounded-xl p-1 flex">
              <button
                onClick={() => setActiveTab('github')}
                className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 flex items-center gap-2 ${
                  activeTab === 'github'
                    ? 'bg-gradient-to-r from-neon-blue to-neon-purple text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-white/10'
                }`}
              >
                <Github className="h-5 w-5" />
                GitHub Repository
              </button>
              <button
                onClick={() => setActiveTab('upload')}
                className={`px-6 py-3 rounded-lg font-semibold transition-all duration-300 flex items-center gap-2 ${
                  activeTab === 'upload'
                    ? 'bg-gradient-to-r from-neon-blue to-neon-purple text-white shadow-lg'
                    : 'text-gray-300 hover:text-white hover:bg-white/10'
                }`}
              >
                <Upload className="h-5 w-5" />
                Upload Files
              </button>
            </div>
          </div>

          {/* Content Area */}
          <div className="glass rounded-2xl p-8">
            {activeTab === 'github' ? (
              <GitHubAnalysisForm
                onAnalysisStart={(jobId) => {
                  window.location.href = `/dashboard?jobId=${jobId}`
                }}
                onError={(error) => {
                  console.error('Analysis error:', error)
                  // Could show a toast notification here
                }}
              />
            ) : (
              <FileUploadForm
                onAnalysisStart={(jobId) => {
                  window.location.href = `/dashboard?jobId=${jobId}`
                }}
                onError={(error) => {
                  console.error('Upload error:', error)
                  // Could show a toast notification here
                }}
              />
            )}
          </div>
        </div>

        {/* Features Grid */}
        <div className="grid md:grid-cols-3 gap-8 mb-16">
          <div className="glass rounded-2xl p-8 text-center">
            <Shield className="h-12 w-12 text-red-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-3">Security Analysis</h3>
            <p className="text-gray-400">
              Detect vulnerabilities, security anti-patterns, and potential exploits in your code
            </p>
          </div>

          <div className="glass rounded-2xl p-8 text-center">
            <Zap className="h-12 w-12 text-yellow-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-3">Performance Insights</h3>
            <p className="text-gray-400">
              Identify bottlenecks, inefficient algorithms, and optimization opportunities
            </p>
          </div>

          <div className="glass rounded-2xl p-8 text-center">
            <Target className="h-12 w-12 text-green-400 mx-auto mb-4" />
            <h3 className="text-xl font-semibold mb-3">Code Quality</h3>
            <p className="text-gray-400">
              Measure complexity, detect duplication, and improve maintainability
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="text-center">
          <h2 className="text-3xl font-bold mb-6">Ready to improve your code?</h2>
          <div className="flex justify-center space-x-4">
            <Link
              href="/dashboard"
              className="bg-gradient-to-r from-neon-blue to-neon-purple text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300"
            >
              View Dashboard
            </Link>
            <Link
              href="/chat"
              className="glass border border-white/20 text-white px-8 py-3 rounded-lg font-semibold hover:bg-white/10 transition-all duration-300 flex items-center space-x-2"
            >
              <MessageCircle className="h-5 w-5" />
              <span>Ask AI</span>
            </Link>
          </div>
        </div>
      </div>
    </div>
  )
}