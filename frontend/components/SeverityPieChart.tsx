'use client'

import { useEffect, useRef } from 'react'

interface SeverityPieChartProps {
  data: Record<string, number>
}

const SEVERITY_COLORS = {
  critical: '#ef4444', // red-500
  high: '#f97316',     // orange-500
  medium: '#eab308',   // yellow-500
  low: '#22c55e'       // green-500
}

export default function SeverityPieChart({ data }: SeverityPieChartProps) {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return

    const ctx = canvas.getContext('2d')
    if (!ctx) return

    // Clear canvas
    ctx.clearRect(0, 0, canvas.width, canvas.height)

    const centerX = canvas.width / 2
    const centerY = canvas.height / 2
    const radius = Math.min(centerX, centerY) - 20

    const entries = Object.entries(data)
    const total = entries.reduce((sum, [, value]) => sum + value, 0)

    if (total === 0) return

    let startAngle = -Math.PI / 2 // Start from top

    entries.forEach(([severity, value]) => {
      const percentage = value / total
      const endAngle = startAngle + (percentage * 2 * Math.PI)

      // Draw pie slice
      ctx.beginPath()
      ctx.moveTo(centerX, centerY)
      ctx.arc(centerX, centerY, radius, startAngle, endAngle)
      ctx.closePath()
      ctx.fillStyle = SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS] || '#6b7280'
      ctx.fill()

      // Draw border
      ctx.strokeStyle = '#ffffff'
      ctx.lineWidth = 2
      ctx.stroke()

      startAngle = endAngle
    })

    // Draw center circle for donut effect
    ctx.beginPath()
    ctx.arc(centerX, centerY, radius * 0.6, 0, 2 * Math.PI)
    ctx.fillStyle = '#1f2937'
    ctx.fill()

    // Draw total in center
    ctx.fillStyle = '#ffffff'
    ctx.font = 'bold 16px Inter, sans-serif'
    ctx.textAlign = 'center'
    ctx.fillText(total.toString(), centerX, centerY - 5)
    ctx.font = '12px Inter, sans-serif'
    ctx.fillText('Total Issues', centerX, centerY + 10)

  }, [data])

  return (
    <div className="bg-dark-surface rounded-lg overflow-hidden shadow-lg border border-white/10">
      <div className="px-6 py-4 bg-gradient-to-r from-gray-800 to-gray-700 border-b border-white/10">
        <h4 className="text-lg font-semibold text-white">Visual Distribution</h4>
        <p className="text-sm text-gray-400 mt-1">Interactive pie chart showing issue severity breakdown</p>
      </div>
      <div className="p-6">
        <div className="flex flex-col items-center">
          <canvas
            ref={canvasRef}
            width={300}
            height={300}
            className="max-w-full h-auto mb-6"
          />
          <div className="w-full">
            <h5 className="text-sm font-semibold text-white mb-4 text-center uppercase tracking-wide">Legend</h5>
            <div className="grid grid-cols-2 gap-3">
              {Object.entries(data).map(([severity, count]) => {
                const severityColors = {
                  critical: 'text-red-400 border-red-400',
                  high: 'text-orange-400 border-orange-400',
                  medium: 'text-yellow-400 border-yellow-400',
                  low: 'text-green-400 border-green-400'
                }
                const bgColors = {
                  critical: 'bg-red-500/10 hover:bg-red-500/20',
                  high: 'bg-orange-500/10 hover:bg-orange-500/20',
                  medium: 'bg-yellow-500/10 hover:bg-yellow-500/20',
                  low: 'bg-green-500/10 hover:bg-green-500/20'
                }

                return (
                  <div key={severity} className={`flex items-center justify-between p-3 rounded-lg border border-white/5 ${bgColors[severity as keyof typeof bgColors]} transition-colors duration-200`}>
                    <div className="flex items-center gap-3">
                      <div
                        className={`w-4 h-4 rounded-full border-2 ${severityColors[severity as keyof typeof severityColors]}`}
                        style={{ backgroundColor: SEVERITY_COLORS[severity as keyof typeof SEVERITY_COLORS] || '#6b7280' }}
                      />
                      <span className={`font-semibold text-sm capitalize ${severityColors[severity as keyof typeof severityColors]}`}>
                        {severity}
                      </span>
                    </div>
                    <div className="flex items-center gap-2">
                      <span className="text-white font-bold text-lg">
                        {count}
                      </span>
                      <div className={`w-8 h-2 rounded-full ${bgColors[severity as keyof typeof bgColors]}`}>
                        <div
                          className={`h-full rounded-full ${severityColors[severity as keyof typeof severityColors].replace('text-', 'bg-').replace('border-', 'bg-')}`}
                          style={{ width: `${count > 0 ? Math.max((count / Object.values(data).reduce((a, b) => a + b, 0)) * 100, 10) : 0}%` }}
                        ></div>
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}