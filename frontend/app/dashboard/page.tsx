'use client'

import { useState, useEffect } from 'react'
import { AlertTriangle, Shield, Zap, Code, FileText, TrendingUp } from 'lucide-react'

interface Issue {
  id: string
  category: string
  severity: string
  title: string
  description: string
  file_path: string
  line_number?: number
  suggestion: string
  impact_score: number
}

interface AnalysisResult {
  summary: {
    total_issues: number
    severity_breakdown: Record<string, number>
    category_breakdown: Record<string, number>
    average_complexity: number
    languages_detected: string[]
  }
  issues: Issue[]
  total_files: number
  total_lines: number
}

export default function Dashboard() {
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null)
  const [loading, setLoading] = useState(false)
  const [selectedSeverity, setSelectedSeverity] = useState<string>('all')

  const severityColors = {
    critical: 'text-red-400 bg-red-400/10 border-red-400/20',
    high: 'text-orange-400 bg-orange-400/10 border-orange-400/20',
    medium: 'text-yellow-400 bg-yellow-400/10 border-yellow-400/20',
    low: 'text-green-400 bg-green-400/10 border-green-400/20'
  }

  const categoryIcons = {
    security: Shield,
    performance: Zap,
    complexity: Code,
    duplication: FileText,
    style: TrendingUp
  }

  const filteredIssues = analysisResult?.issues.filter(issue => 
    selectedSeverity === 'all' || issue.severity === selectedSeverity
  ) || []

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
            <span className="text-white font-semibold">Dashboard</span>
            <a href="/chat" className="text-gray-300 hover:text-white transition-colors">
              Chat
            </a>
          </div>
        </div>
      </nav>

      <div className="max-w-7xl mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold gradient-text mb-4">Code Analysis Dashboard</h1>
          <p className="text-gray-300">Monitor your code quality metrics and issues</p>
        </div>

        {!analysisResult ? (
          /* Upload Section */
          <div className="glass rounded-2xl p-8 text-center">
            <AlertTriangle className="h-16 w-16 text-yellow-400 mx-auto mb-6" />
            <h3 className="text-2xl font-semibold mb-4">No Analysis Data</h3>
            <p className="text-gray-400 mb-6">
              Upload your code files to see detailed analysis results
            </p>
            <button 
              onClick={() => setLoading(true)}
              className="bg-gradient-to-r from-neon-blue to-neon-purple text-white px-8 py-3 rounded-lg font-semibold hover:shadow-lg transition-all duration-300"
            >
              Upload & Analyze
            </button>
          </div>
        ) : (
          <div className="space-y-8">
            {/* Summary Cards */}
            <div className="grid md:grid-cols-4 gap-6">
              <div className="glass rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Total Issues</p>
                    <p className="text-3xl font-bold text-white">{analysisResult.summary.total_issues}</p>
                  </div>
                  <AlertTriangle className="h-8 w-8 text-red-400" />
                </div>
              </div>
              
              <div className="glass rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Files Analyzed</p>
                    <p className="text-3xl font-bold text-white">{analysisResult.total_files}</p>
                  </div>
                  <FileText className="h-8 w-8 text-blue-400" />
                </div>
              </div>
              
              <div className="glass rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Lines of Code</p>
                    <p className="text-3xl font-bold text-white">{analysisResult.total_lines.toLocaleString()}</p>
                  </div>
                  <Code className="h-8 w-8 text-green-400" />
                </div>
              </div>
              
              <div className="glass rounded-xl p-6">
                <div className="flex items-center justify-between">
                  <div>
                    <p className="text-gray-400 text-sm">Avg Complexity</p>
                    <p className="text-3xl font-bold text-white">{analysisResult.summary.average_complexity.toFixed(1)}</p>
                  </div>
                  <TrendingUp className="h-8 w-8 text-purple-400" />
                </div>
              </div>
            </div>  
          {/* Severity Filter */}
            <div className="glass rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-4">Filter by Severity</h3>
              <div className="flex space-x-2">
                {['all', 'critical', 'high', 'medium', 'low'].map(severity => (
                  <button
                    key={severity}
                    onClick={() => setSelectedSeverity(severity)}
                    className={`px-4 py-2 rounded-lg font-medium transition-all ${
                      selectedSeverity === severity
                        ? 'bg-neon-blue text-white'
                        : 'bg-white/10 text-gray-300 hover:bg-white/20'
                    }`}
                  >
                    {severity.charAt(0).toUpperCase() + severity.slice(1)}
                    {severity !== 'all' && (
                      <span className="ml-2 text-xs">
                        ({analysisResult.summary.severity_breakdown[severity] || 0})
                      </span>
                    )}
                  </button>
                ))}
              </div>
            </div>

            {/* Issues List */}
            <div className="glass rounded-xl p-6">
              <h3 className="text-xl font-semibold mb-6">
                Issues ({filteredIssues.length})
              </h3>
              
              <div className="space-y-4">
                {filteredIssues.map(issue => {
                  const IconComponent = categoryIcons[issue.category as keyof typeof categoryIcons] || AlertTriangle
                  const severityClass = severityColors[issue.severity as keyof typeof severityColors]
                  
                  return (
                    <div key={issue.id} className="bg-white/5 rounded-lg p-4 border border-white/10">
                      <div className="flex items-start space-x-4">
                        <div className={`p-2 rounded-lg ${severityClass}`}>
                          <IconComponent className="h-5 w-5" />
                        </div>
                        
                        <div className="flex-1">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-semibold text-white">{issue.title}</h4>
                            <span className={`px-2 py-1 rounded text-xs font-medium ${severityClass}`}>
                              {issue.severity.toUpperCase()}
                            </span>
                          </div>
                          
                          <p className="text-gray-300 mb-2">{issue.description}</p>
                          
                          <div className="flex items-center justify-between text-sm text-gray-400">
                            <span>📁 {issue.file_path}:{issue.line_number || 'N/A'}</span>
                            <span>Impact: {issue.impact_score}/10</span>
                          </div>
                          
                          <div className="mt-3 p-3 bg-blue-500/10 rounded border-l-4 border-blue-400">
                            <p className="text-sm text-blue-200">
                              💡 <strong>Suggestion:</strong> {issue.suggestion}
                            </p>
                          </div>
                        </div>
                      </div>
                    </div>
                  )
                })}
                
                {filteredIssues.length === 0 && (
                  <div className="text-center py-8 text-gray-400">
                    No issues found for the selected severity level.
                  </div>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  )
}