'use client'

import { useState } from 'react'
import { Download, FileText, AlertCircle, CheckCircle, Info, X } from 'lucide-react'
import { AnalysisStatus, apiService } from '../utils/apiService'
import DependencyGraph from './DependencyGraph'
import SeverityPieChart from './SeverityPieChart'

interface AnalysisResultsProps {
  results: AnalysisStatus
  onNewAnalysis: () => void
}

export default function AnalysisResults({ results, onNewAnalysis }: AnalysisResultsProps) {
  const [activeTab, setActiveTab] = useState<'overview' | 'issues' | 'dependencies'>('overview')

  // Debug logging
  console.log('AnalysisResults received:', results)
  console.log('Issues data:', results.issues)
  console.log('Dependency graph data:', results.dependency_graph)

  // Calculate summary stats from issues data
  const calculateSummary = () => {
    if (!results.issues || results.issues.length === 0) {
      return {
        totalFiles: 0,
        criticalIssues: 0,
        totalIssues: 0,
        qualityScore: 10,
        severityBreakdown: {}
      }
    }

    const totalIssues = results.issues.length
    const criticalIssues = results.issues.filter(issue => issue.severity.toLowerCase() === 'critical').length

    // Calculate impact score based on severity levels
    const getImpactScore = (severity: string) => {
      switch (severity.toLowerCase()) {
        case 'critical': return 9.0
        case 'high': return 7.0
        case 'medium': return 5.0
        case 'low': return 3.0
        default: return 5.0
      }
    }

    const totalImpactScore = results.issues.reduce((sum, issue) => sum + getImpactScore(issue.severity), 0)
    const qualityScore = Math.max(0, Math.round((10 - (totalImpactScore / totalIssues)) * 10) / 10)

    // Count unique files
    const uniqueFiles = new Set(results.issues.map(issue => issue.file)).size

    // Calculate severity breakdown
    const severityBreakdown: Record<string, number> = {}
    results.issues.forEach(issue => {
      const severity = issue.severity.toLowerCase()
      severityBreakdown[severity] = (severityBreakdown[severity] || 0) + 1
    })

    return {
      totalFiles: uniqueFiles,
      criticalIssues,
      totalIssues,
      qualityScore,
      severityBreakdown
    }
  }

  const summary = calculateSummary()

  const handleDownloadReport = async () => {
    try {
      const blob = await apiService.generateReport(results.job_id, 'html')
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `code-quality-report-${results.job_id}.html`
      document.body.appendChild(a)
      a.click()
      window.URL.revokeObjectURL(url)
      document.body.removeChild(a)
    } catch (error) {
      console.error('Failed to download report:', error)
      // Fallback: try to generate a simple HTML report
      generateFallbackReport()
    }
  }

  const generateFallbackReport = () => {
    const reportHtml = `
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Code Quality Report - ${results.job_id}</title>
    <style>
        body { font-family: 'Inter', sans-serif; background: #0f172a; color: #ffffff; margin: 0; padding: 20px; }
        .container { max-width: 1200px; margin: 0 auto; }
        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 30px; border-radius: 10px; margin-bottom: 30px; }
        .stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 20px; margin-bottom: 30px; }
        .stat-card { background: #1e293b; padding: 20px; border-radius: 10px; text-align: center; }
        .issues { margin-bottom: 30px; }
        .issue { background: #1e293b; padding: 15px; margin-bottom: 10px; border-radius: 8px; border-left: 4px solid; }
        .critical { border-left-color: #ef4444; }
        .high { border-left-color: #f97316; }
        .medium { border-left-color: #eab308; }
        .low { border-left-color: #22c55e; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Code Quality Analysis Report</h1>
            <p>Job ID: ${results.job_id}</p>
            <p>Generated: ${new Date().toLocaleString()}</p>
        </div>

        <div class="stats">
            <div class="stat-card">
                <h3>${summary.totalIssues}</h3>
                <p>Total Issues</p>
            </div>
            <div class="stat-card">
                <h3>${summary.qualityScore}/10</h3>
                <p>Quality Score</p>
            </div>
            <div class="stat-card">
                <h3>${summary.totalFiles}</h3>
                <p>Files Analyzed</p>
            </div>
            <div class="stat-card">
                <h3>${summary.criticalIssues}</h3>
                <p>Critical Issues</p>
            </div>
        </div>

        <div class="issues">
            <h2>Issues Found</h2>
            ${results.issues?.map(issue => `
                <div class="issue ${issue.severity.toLowerCase()}">
                    <h3>${issue.severity.toUpperCase()}: ${issue.message}</h3>
                    <p><strong>File:</strong> ${issue.file}</p>
                    ${issue.line ? `<p><strong>Line:</strong> ${issue.line}</p>` : ''}
                    ${issue.suggestion ? `<p><strong>Suggestion:</strong> ${issue.suggestion}</p>` : ''}
                </div>
            `).join('') || '<p>No issues found.</p>'}
        </div>
    </div>
</body>
</html>`

    const blob = new Blob([reportHtml], { type: 'text/html' })
    const url = window.URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `code-quality-report-${results.job_id}.html`
    document.body.appendChild(a)
    a.click()
    window.URL.revokeObjectURL(url)
    document.body.removeChild(a)
  }

  const getSeverityIcon = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return <AlertCircle className="h-5 w-5 text-red-400" />
      case 'medium':
        return <Info className="h-5 w-5 text-yellow-400" />
      case 'low':
        return <CheckCircle className="h-5 w-5 text-green-400" />
      default:
        return <Info className="h-5 w-5 text-gray-400" />
    }
  }

  const getSeverityColor = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical':
      case 'high':
        return 'text-red-400'
      case 'medium':
        return 'text-yellow-400'
      case 'low':
        return 'text-green-400'
      default:
        return 'text-gray-400'
    }
  }

  const getNodeColor = (fileType: string) => {
    switch (fileType.toLowerCase()) {
      case 'python':
        return '#3776ab' // Python blue
      case 'javascript':
      case 'typescript':
        return '#f7df1e' // JavaScript yellow
      case 'html':
        return '#e34f26' // HTML orange
      case 'css':
        return '#1572b6' // CSS blue
      case 'json':
        return '#000000' // JSON black
      case 'markdown':
        return '#083fa1' // Markdown blue
      default:
        return '#6b7280' // Gray for unknown types
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="glass rounded-xl p-6">
        <div className="flex justify-between items-start mb-4">
          <div>
            <h2 className="text-3xl font-bold mb-2">Analysis Complete</h2>
            <p className="text-gray-400">
              Code quality analysis finished successfully
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={handleDownloadReport}
              className="flex items-center gap-2 bg-gradient-to-r from-neon-blue to-neon-purple text-white px-4 py-2 rounded-lg font-semibold hover:shadow-lg transition-all duration-300"
            >
              <Download className="h-4 w-4" />
              Download Report
            </button>
            <button
              onClick={onNewAnalysis}
              className="flex items-center gap-2 bg-white/10 text-white px-4 py-2 rounded-lg font-semibold hover:bg-white/20 transition-all duration-300"
            >
              <FileText className="h-4 w-4" />
              New Analysis
            </button>
          </div>
        </div>

        {/* Summary Stats */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <div className="bg-dark-surface rounded-lg p-4">
            <div className="text-2xl font-bold text-white mb-1">
              {summary.totalFiles}
            </div>
            <div className="text-gray-400 text-sm">Files Analyzed</div>
          </div>
          <div className="bg-dark-surface rounded-lg p-4">
            <div className="text-2xl font-bold text-red-400 mb-1">
              {summary.criticalIssues}
            </div>
            <div className="text-gray-400 text-sm">Critical Issues</div>
          </div>
          <div className="bg-dark-surface rounded-lg p-4">
            <div className="text-2xl font-bold text-yellow-400 mb-1">
              {summary.totalIssues}
            </div>
            <div className="text-gray-400 text-sm">Total Issues</div>
          </div>
          <div className="bg-dark-surface rounded-lg p-4">
            <div className="text-2xl font-bold text-green-400 mb-1">
              {summary.qualityScore}/10
            </div>
            <div className="text-gray-400 text-sm">Quality Score</div>
          </div>
        </div>
      </div>

      {/* Tabs */}
      <div className="glass rounded-xl overflow-hidden">
        <div className="flex border-b border-white/10">
          {[
            { id: 'overview', label: 'Overview' },
            { id: 'issues', label: 'Issues' },
            { id: 'dependencies', label: 'Dependencies' }
          ].map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id as any)}
              className={`px-6 py-4 font-semibold transition-colors duration-200 ${
                activeTab === tab.id
                  ? 'text-neon-blue border-b-2 border-neon-blue'
                  : 'text-gray-400 hover:text-white'
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        <div className="p-6">
          {activeTab === 'overview' && (
            <div className="space-y-6">
              {/* Severity Distribution */}
              {summary.totalIssues > 0 && (
                <div>
                  <h3 className="text-xl font-semibold mb-4">Issue Severity Distribution</h3>
                  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
                    <div className="bg-dark-surface rounded-lg p-6">
                      <SeverityPieChart data={summary.severityBreakdown} />
                    </div>
                    <div className="bg-dark-surface rounded-lg overflow-hidden shadow-lg">
                      <div className="px-6 py-4 bg-gradient-to-r from-gray-800 to-gray-700 border-b border-white/10">
                        <h4 className="text-lg font-semibold text-white">Severity Breakdown</h4>
                        <p className="text-sm text-gray-400 mt-1">Detailed issue distribution by severity level</p>
                      </div>
                      <table className="w-full">
                        <thead className="bg-gradient-to-r from-gray-800/50 to-gray-700/50">
                          <tr>
                            <th className="px-6 py-4 text-left text-sm font-bold text-white uppercase tracking-wide w-1/3">
                              <div className="flex items-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-gray-400"></div>
                                Severity
                              </div>
                            </th>
                            <th className="px-6 py-4 text-center text-sm font-bold text-white uppercase tracking-wide w-1/3">
                              <div className="flex items-center justify-center gap-2">
                                <div className="w-2 h-2 rounded-full bg-blue-400"></div>
                                Count
                              </div>
                            </th>
                            <th className="px-6 py-4 text-right text-sm font-bold text-white uppercase tracking-wide w-1/3">
                              <div className="flex items-center justify-end gap-2">
                                <div className="w-2 h-2 rounded-full bg-green-400"></div>
                                Percentage
                              </div>
                            </th>
                          </tr>
                        </thead>
                      <tbody className="divide-y divide-white/5">
                        {['critical', 'high', 'medium', 'low'].map(severity => {
                          const count = summary.severityBreakdown[severity] || 0
                          const percentage = summary.totalIssues > 0 ? ((count / summary.totalIssues) * 100) : 0
                          const severityColors = {
                            critical: 'text-red-400 border-red-400',
                            high: 'text-orange-400 border-orange-400',
                            medium: 'text-yellow-400 border-yellow-400',
                            low: 'text-green-400 border-green-400'
                          }
                          const bgColors = {
                            critical: 'bg-red-500/10',
                            high: 'bg-orange-500/10',
                            medium: 'bg-yellow-500/10',
                            low: 'bg-green-500/10'
                          }

                          return (
                            <tr key={severity} className={`hover:${bgColors[severity as keyof typeof bgColors]} transition-colors duration-200`}>
                              <td className="px-6 py-4 whitespace-nowrap">
                                <div className="flex items-center gap-3">
                                  <div className={`w-3 h-3 rounded-full border-2 ${severityColors[severity as keyof typeof severityColors]}`}></div>
                                  <span className={`font-bold uppercase text-sm ${severityColors[severity as keyof typeof severityColors]}`}>
                                    {severity}
                                  </span>
                                </div>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-center">
                                <span className="text-white font-bold text-lg">
                                  {count}
                                </span>
                              </td>
                              <td className="px-6 py-4 whitespace-nowrap text-right">
                                <div className="flex items-center justify-end gap-2">
                                  <span className="text-white font-semibold">
                                    {percentage.toFixed(1)}%
                                  </span>
                                  <div className={`w-12 h-2 rounded-full ${bgColors[severity as keyof typeof bgColors]}`}>
                                    <div
                                      className={`h-full rounded-full ${severityColors[severity as keyof typeof severityColors].replace('text-', 'bg-').replace('border-', 'bg-')}`}
                                      style={{ width: `${percentage}%` }}
                                    ></div>
                                  </div>
                                </div>
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                      <tfoot className="bg-gradient-to-r from-gray-800/30 to-gray-700/30 border-t border-white/10">
                        <tr>
                          <td className="px-6 py-4 whitespace-nowrap">
                            <div className="flex items-center gap-3">
                              <div className="w-3 h-3 rounded-full bg-gradient-to-r from-blue-400 to-purple-400"></div>
                              <span className="font-bold text-white uppercase text-sm">Total</span>
                            </div>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-center">
                            <span className="text-white font-bold text-lg text-blue-400">
                              {summary.totalIssues}
                            </span>
                          </td>
                          <td className="px-6 py-4 whitespace-nowrap text-right">
                            <div className="flex items-center justify-end gap-2">
                              <span className="text-white font-bold">
                                100.0%
                              </span>
                              <div className="w-12 h-2 rounded-full bg-gradient-to-r from-blue-500/20 to-purple-500/20">
                                <div className="h-full rounded-full bg-gradient-to-r from-blue-400 to-purple-400" style={{ width: '100%' }}></div>
                              </div>
                            </div>
                          </td>
                        </tr>
                      </tfoot>
                    </table>
                    </div>
                  </div>
                </div>
              )}

              {/* Top Issues */}
              {results.issues && results.issues.length > 0 && (
                <div>
                  <h3 className="text-xl font-semibold mb-4">Top Issues</h3>
                  <div className="space-y-3">
                    {results.issues.slice(0, 5).map((issue, index) => (
                      <div key={index} className="bg-dark-surface rounded-lg p-4">
                        <div className="flex items-start gap-3">
                          {getSeverityIcon(issue.severity)}
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className={`font-semibold ${getSeverityColor(issue.severity)}`}>
                                {issue.severity}
                              </span>
                              <span className="text-gray-400">•</span>
                              <span className="text-gray-400 text-sm">{issue.file}</span>
                            </div>
                            <p className="text-white">{issue.message}</p>
                            {issue.line && (
                              <p className="text-gray-400 text-sm mt-1">
                                Line {issue.line}
                              </p>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'issues' && (
            <div className="space-y-4">
              {results.issues && results.issues.length > 0 ? (
                results.issues.map((issue, index) => (
                  <div key={index} className="bg-dark-surface rounded-lg p-4">
                    <div className="flex items-start gap-3">
                      {getSeverityIcon(issue.severity)}
                      <div className="flex-1">
                        <div className="flex items-center gap-2 mb-2">
                          <span className={`font-semibold ${getSeverityColor(issue.severity)}`}>
                            {issue.severity}
                          </span>
                          <span className="text-gray-400">•</span>
                          <span className="text-gray-400 text-sm">{issue.file}</span>
                          {issue.line && (
                            <>
                              <span className="text-gray-400">•</span>
                              <span className="text-gray-400 text-sm">Line {issue.line}</span>
                            </>
                          )}
                        </div>
                        <p className="text-white mb-2">{issue.message}</p>
                        {issue.suggestion && (
                          <div className="bg-blue-500/10 border border-blue-500/20 rounded-lg p-3">
                            <p className="text-blue-200 text-sm">
                              <strong>Suggestion:</strong> {issue.suggestion}
                            </p>
                          </div>
                        )}
                      </div>
                    </div>
                  </div>
                ))
              ) : (
                <div className="text-center py-12">
                  <CheckCircle className="h-16 w-16 text-green-400 mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">No Issues Found</h3>
                  <p className="text-gray-400">
                    Great job! Your code appears to be clean and well-structured.
                  </p>
                </div>
              )}
            </div>
          )}

          {activeTab === 'dependencies' && (
            <div>
              {results.dependency_graph ? (
                <div className="text-center py-12">
                  <Info className="h-16 w-16 text-neon-blue mx-auto mb-4" />
                  <h3 className="text-xl font-semibold mb-2">Dependency Graph</h3>
                  <p className="text-gray-400 mb-4">
                    Found {results.dependency_graph.nodes?.length || 0} files with {results.dependency_graph.links?.length || 0} relationships
                  </p>
                  <div className="bg-dark-surface rounded-lg p-4 max-h-96 overflow-auto">
                    <div className="space-y-4">
                      {results.dependency_graph.nodes?.map((node, index) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-white/5 rounded">
                          <div className="flex items-center space-x-3">
                            <div
                              className="w-3 h-3 rounded-full"
                              style={{ backgroundColor: getNodeColor(node.type) }}
                            />
                            <span className="text-white font-mono text-sm">{node.name || node.id}</span>
                          </div>
                          <span className="text-gray-400 text-sm">Size: {node.size}</span>
                        </div>
                      ))}
                    </div>
                  </div>
                </div>
              ) : (
                <DependencyGraph jobId={results.job_id} />
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  )
}