'use client'

import { PieChart, Pie, Cell, ResponsiveContainer, Tooltip, Legend } from 'recharts'
import { AlertTriangle, Shield, Zap, Code } from 'lucide-react'

interface SeverityDistributionProps {
  severityBreakdown: Record<string, number>
  totalIssues: number
}

const COLORS = {
  critical: '#ef4444',
  high: '#f97316',
  medium: '#eab308',
  low: '#22c55e'
}

const ICONS = {
  critical: AlertTriangle,
  high: Shield,
  medium: Zap,
  low: Code
}

export default function SeverityDistribution({ severityBreakdown, totalIssues }: SeverityDistributionProps) {
  const data = Object.entries(severityBreakdown).map(([severity, count]) => ({
    name: severity.charAt(0).toUpperCase() + severity.slice(1),
    value: count,
    percentage: totalIssues > 0 ? Math.round((count / totalIssues) * 100) : 0,
    color: COLORS[severity as keyof typeof COLORS] || '#6b7280'
  }))

  const CustomTooltip = ({ active, payload }: any) => {
    if (active && payload && payload.length) {
      const data = payload[0].payload
      return (
        <div className="bg-dark-surface border border-white/20 rounded-lg p-3 shadow-lg">
          <p className="text-white font-semibold">{data.name} Severity</p>
          <p className="text-gray-300">{data.value} issues ({data.percentage}%)</p>
        </div>
      )
    }
    return null
  }

  const renderCustomizedLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percentage }: any) => {
    if (percentage < 5) return null // Don't show labels for small slices

    const RADIAN = Math.PI / 180
    const radius = innerRadius + (outerRadius - innerRadius) * 0.5
    const x = cx + radius * Math.cos(-midAngle * RADIAN)
    const y = cy + radius * Math.sin(-midAngle * RADIAN)

    return (
      <text
        x={x}
        y={y}
        fill="white"
        textAnchor={x > cx ? 'start' : 'end'}
        dominantBaseline="central"
        fontSize="12"
        fontWeight="bold"
      >
        {`${percentage}%`}
      </text>
    )
  }

  return (
    <div className="glass rounded-xl p-6">
      <h3 className="text-xl font-semibold mb-6 gradient-text">Issue Severity Distribution</h3>

      <div className="grid md:grid-cols-2 gap-6">
        {/* Chart */}
        <div className="h-64">
          <ResponsiveContainer width="100%" height="100%">
            <PieChart>
              <Pie
                data={data}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={renderCustomizedLabel}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {data.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={entry.color} />
                ))}
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
        </div>

        {/* Legend */}
        <div className="space-y-3">
          {data.map((item) => {
            const IconComponent = ICONS[item.name.toLowerCase() as keyof typeof ICONS] || AlertTriangle
            return (
              <div key={item.name} className="flex items-center justify-between">
                <div className="flex items-center space-x-3">
                  <div
                    className="w-4 h-4 rounded-full"
                    style={{ backgroundColor: item.color }}
                  />
                  <IconComponent className="h-5 w-5" style={{ color: item.color }} />
                  <span className="text-white font-medium">{item.name}</span>
                </div>
                <div className="text-right">
                  <div className="text-white font-semibold">{item.value}</div>
                  <div className="text-gray-400 text-sm">{item.percentage}%</div>
                </div>
              </div>
            )
          })}
        </div>
      </div>

      {/* Summary */}
      <div className="mt-6 pt-4 border-t border-white/10">
        <div className="flex items-center justify-between text-sm">
          <span className="text-gray-400">Total Issues:</span>
          <span className="text-white font-semibold">{totalIssues}</span>
        </div>
        <div className="flex items-center justify-between text-sm mt-1">
          <span className="text-gray-400">Most Critical:</span>
          <span className="text-red-400 font-semibold">
            {data.find(d => d.name === 'Critical')?.value || 0} Critical
          </span>
        </div>
      </div>
    </div>
  )
}