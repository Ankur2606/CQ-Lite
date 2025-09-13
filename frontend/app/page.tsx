'use client'

import { useState } from 'react'
import { Upload, Code, MessageCircle, Zap, Shield, Target } from 'lucide-react'
import Link from 'next/link'

export default function Home() {
  const [dragActive, setDragActive] = useState(false)

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
      // Handle file upload
      console.log('Files dropped:', e.dataTransfer.files)
    }
  }

  return (
    <div className="min-h-screen">
      {/* Navigation */}
      <nav className="glass border-b border-white/10 p-4">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div className="flex items-center space-x-2">
            <Code className="h-8 w-8 text-neon-blue" />
            <span className="text-xl font-bold gradient-text">CodeQuality AI</span>
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
            Code Quality Intelligence
          </h1>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-8">
            Analyze your codebase with advanced AST-based analytics, detect security vulnerabilities, 
            performance issues, and get AI-powered insights to improve your code quality.
          </p>
        </div>

        {/* Upload Area */}
        <div className="max-w-4xl mx-auto mb-16">
          <div
            className={`gradient-border rounded-2xl p-8 text-center transition-all duration-300 ${
              dragActive ? 'scale-105 shadow-2xl' : ''
            }`}
            onDragEnter={handleDrag}
            onDragLeave={handleDrag}
            onDragOver={handleDrag}
            onDrop={handleDrop}
          >
            <div className="bg-dark-surface rounded-xl p-12">
              <Upload className="h-16 w-16 text-neon-blue mx-auto mb-6" />
              <h3 className="text-2xl font-semibold mb-4">Upload Your Code</h3>
              <p className="text-gray-400 mb-6">
                Drag and drop your files here, or click to browse
              </p>
              <button className="bg-gradient-to-r from-neon-blue to-neon-purple text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300">
                Choose Files
              </button>
            </div>
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
              Start Analysis
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