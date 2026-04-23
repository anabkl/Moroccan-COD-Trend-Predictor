import React from 'react'
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell
} from 'recharts'

const RANGES = [
  { label: '0–39',  min: 0,  max: 39,  color: '#ef4444' },
  { label: '40–59', min: 40, max: 59,  color: '#eab308' },
  { label: '60–79', min: 60, max: 79,  color: '#3b82f6' },
  { label: '80–100', min: 80, max: 100, color: '#22c55e' }
]

function buildChartData(products) {
  return RANGES.map((range) => ({
    ...range,
    count: products.filter(
      (p) => (p.trend_score || 0) >= range.min && (p.trend_score || 0) <= range.max
    ).length
  }))
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div className="bg-white border border-gray-200 rounded-lg shadow-lg p-3 text-sm">
        <p className="font-semibold text-gray-700">Score {label}</p>
        <p className="text-gray-600">{payload[0].value} product(s)</p>
      </div>
    )
  }
  return null
}

export default function ScoreDistributionChart({ products = [] }) {
  const data = buildChartData(products)

  return (
    <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
      <h3 className="text-base font-semibold text-gray-800 mb-4">Score Distribution</h3>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={data} margin={{ top: 5, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
          <XAxis dataKey="label" tick={{ fontSize: 12, fill: '#6b7280' }} />
          <YAxis allowDecimals={false} tick={{ fontSize: 12, fill: '#6b7280' }} />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="count" radius={[6, 6, 0, 0]}>
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={entry.color} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
