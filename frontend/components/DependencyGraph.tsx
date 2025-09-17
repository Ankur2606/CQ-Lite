'use client'

import { useState, useEffect } from 'react'
import { Network, FileText, AlertTriangle } from 'lucide-react'
import { apiService } from '../utils/apiService'

interface DependencyGraphProps {
  jobId: string
}

interface Node {
  id: string
  name?: string
  group: number
  type: string
  size: number
  x?: number
  y?: number
}

interface Link {
  source: string
  target: string
  value: number
}

const FILE_TYPE_COLORS = {
  python: '#3776AB',
  javascript: '#F7DF1E',
  typescript: '#007ACC',
  java: '#ED8B00',
  cpp: '#00599C',
  go: '#00ADD8',
  default: '#6B7280'
}

export default function DependencyGraph({ jobId }: DependencyGraphProps) {
  const [graphData, setGraphData] = useState<{ nodes: Node[]; links: Link[] } | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [selectedNode, setSelectedNode] = useState<Node | null>(null)
  const [hoveredNode, setHoveredNode] = useState<{ node: Node; x: number; y: number } | null>(null)

  useEffect(() => {
    const fetchGraphData = async () => {
      try {
        setLoading(true)
        const response = await apiService.getDependencyGraph(jobId)
        setGraphData(response.dependency_graph)
      } catch (err: any) {
        setError(err.message || 'Failed to load dependency graph')
      } finally {
        setLoading(false)
      }
    }

    if (jobId) {
      fetchGraphData()
    }
  }, [jobId])

  const getNodeColor = (nodeType: string) => {
    const type = nodeType.toLowerCase()
    return FILE_TYPE_COLORS[type as keyof typeof FILE_TYPE_COLORS] || FILE_TYPE_COLORS.default
  }

  const getNodeSize = (size: number) => {
    return Math.max(25, Math.min(60, size * 1.5))
  }

  if (loading) {
    return (
      <div className="glass rounded-xl p-8 text-center">
        <Network className="h-16 w-16 text-neon-blue mx-auto mb-4 animate-pulse" />
        <h3 className="text-xl font-semibold mb-2">Loading Dependency Graph</h3>
        <p className="text-gray-400">Analyzing file relationships...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="glass rounded-xl p-8 text-center">
        <AlertTriangle className="h-16 w-16 text-red-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold mb-2">Failed to Load Graph</h3>
        <p className="text-gray-400">{error}</p>
      </div>
    )
  }

  if (!graphData || graphData.nodes.length === 0) {
    return (
      <div className="glass rounded-xl p-8 text-center">
        <Network className="h-16 w-16 text-gray-400 mx-auto mb-4" />
        <h3 className="text-xl font-semibold mb-2">No Dependencies Found</h3>
        <p className="text-gray-400">The analyzed files don't have clear import relationships.</p>
      </div>
    )
  }

  return (
    <div className="glass rounded-xl p-6">
      <div className="flex items-center space-x-3 mb-6">
        <Network className="h-6 w-6 text-neon-blue" />
        <h3 className="text-xl font-semibold gradient-text">Dependency Graph</h3>
        <span className="text-sm text-gray-400">
          {graphData.nodes.length} files, {graphData.links.length} relationships
        </span>
      </div>

      <div className="grid md:grid-cols-3 gap-6">
        {/* Graph Visualization */}
        <div className="md:col-span-2">
          <div className="bg-dark-surface rounded-lg p-4 h-[500px] overflow-hidden">
            <svg width="100%" height="100%" viewBox="0 0 800 600">
              {/* Render links first */}
              {graphData.links.map((link, index) => {
                const sourceNode = graphData.nodes.find(n => n.id === link.source)
                const targetNode = graphData.nodes.find(n => n.id === link.target)

                if (!sourceNode || !targetNode) return null

                // Improved positioning with better spacing
                const sourceX = (index * 120) % 700 + 50
                const sourceY = Math.floor(index / 6) * 80 + 80
                const targetX = ((index + 1) * 120) % 700 + 50
                const targetY = Math.floor((index + 1) / 6) * 80 + 80

                return (
                  <line
                    key={`link-${index}`}
                    x1={sourceX}
                    y1={sourceY}
                    x2={targetX}
                    y2={targetY}
                    stroke="#4B5563"
                    strokeWidth="2"
                    markerEnd="url(#arrowhead)"
                  />
                )
              })}

              {/* Arrow marker */}
              <defs>
                <marker
                  id="arrowhead"
                  markerWidth="10"
                  markerHeight="7"
                  refX="9"
                  refY="3.5"
                  orient="auto"
                >
                  <polygon
                    points="0 0, 10 3.5, 0 7"
                    fill="#4B5563"
                  />
                </marker>
              </defs>

              {/* Render nodes */}
              {graphData.nodes.map((node, index) => {
                // Improved positioning with better spacing to prevent text collision
                const x = (index * 120) % 700 + 50
                const y = Math.floor(index / 6) * 80 + 80
                const size = getNodeSize(node.size)
                const color = getNodeColor(node.type)

                return (
                  <g key={`node-${node.id}`}>
                    <circle
                      cx={x}
                      cy={y}
                      r={size / 2}
                      fill={color}
                      stroke={selectedNode?.id === node.id ? '#60A5FA' : '#374151'}
                      strokeWidth={selectedNode?.id === node.id ? '3' : '2'}
                      className="cursor-pointer hover:opacity-80 transition-opacity"
                      onClick={() => setSelectedNode(node)}
                      onMouseEnter={(e) => {
                        setHoveredNode({
                          node,
                          x: e.clientX,
                          y: e.clientY
                        })
                      }}
                      onMouseLeave={() => setHoveredNode(null)}
                      onMouseMove={(e) => {
                        if (hoveredNode) {
                          setHoveredNode({
                            ...hoveredNode,
                            x: e.clientX,
                            y: e.clientY
                          })
                        }
                      }}
                    />
                  </g>
                )
              })}
            </svg>

            {/* Hover Tooltip */}
            {hoveredNode && (
              <div
                className="fixed pointer-events-none z-50 bg-gray-900 text-white px-3 py-2 rounded-lg shadow-lg border border-gray-700 max-w-xs"
                style={{
                  left: hoveredNode.x + 15,
                  top: hoveredNode.y - 10,
                  transform: 'translate(0, -100%)'
                }}
              >
                <div className="flex items-center gap-2">
                  <div
                    className="w-3 h-3 rounded-full flex-shrink-0"
                    style={{ backgroundColor: getNodeColor(hoveredNode.node.type) }}
                  />
                  <span className="font-bold text-sm whitespace-nowrap">
                    {hoveredNode.node.name || hoveredNode.node.id}
                  </span>
                </div>
                <div className="text-xs text-gray-300 mt-1 capitalize">
                  {hoveredNode.node.type} • Size: {hoveredNode.node.size}
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Node Details */}
        <div className="space-y-4">
          <h4 className="text-lg font-semibold">File Details</h4>

          {selectedNode ? (
            <div className="bg-dark-surface rounded-lg p-4">
              <div className="flex items-center space-x-3 mb-3">
                <FileText className="h-5 w-5" style={{ color: getNodeColor(selectedNode.type) }} />
                <div>
                  <h5 className="font-semibold text-white">{selectedNode.name || selectedNode.id}</h5>
                  <p className="text-sm text-gray-400 capitalize">{selectedNode.type}</p>
                </div>
              </div>

              <div className="space-y-2">
                <div className="flex justify-between">
                  <span className="text-gray-400">Size:</span>
                  <span className="text-white font-semibold">{selectedNode.size}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-400">Group:</span>
                  <span className="text-white text-sm">{selectedNode.group}</span>
                </div>
              </div>
            </div>
          ) : (
            <div className="bg-dark-surface rounded-lg p-4 text-center">
              <FileText className="h-12 w-12 text-gray-400 mx-auto mb-2" />
              <p className="text-gray-400 text-sm">Click on a node to view details</p>
            </div>
          )}

          {/* Legend */}
          <div className="bg-dark-surface rounded-lg p-4">
            <h5 className="font-semibold mb-3">File Types</h5>
            <div className="space-y-2">
              {Object.entries(FILE_TYPE_COLORS).map(([type, color]) => (
                <div key={type} className="flex items-center space-x-2">
                  <div
                    className="w-3 h-3 rounded-full"
                    style={{ backgroundColor: color }}
                  />
                  <span className="text-sm text-gray-300 capitalize">{type}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}