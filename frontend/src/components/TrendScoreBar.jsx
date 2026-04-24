import React from 'react'

const SCORE_CONFIG = [
  { min: 80, max: 100, color: 'bg-green-500', label: 'Excellent' },
  { min: 60, max: 79,  color: 'bg-blue-500',  label: 'Good' },
  { min: 40, max: 59,  color: 'bg-yellow-500', label: 'Fair' },
  { min: 0,  max: 39,  color: 'bg-red-500',   label: 'Weak' }
]

function getConfig(score) {
  return SCORE_CONFIG.find((c) => score >= c.min && score <= c.max) || SCORE_CONFIG[3]
}

export default function TrendScoreBar({ score = 0, showLabel = false, height = 'h-2' }) {
  const pct = Math.min(100, Math.max(0, score))
  const config = getConfig(pct)

  return (
    <div className="w-full">
      <div className={`w-full bg-gray-200 rounded-full overflow-hidden ${height}`}>
        <div
          className={`${config.color} ${height} rounded-full transition-all duration-700 ease-out`}
          style={{ width: `${pct}%` }}
        />
      </div>
      {showLabel && (
        <div className="flex justify-between mt-1 text-xs text-gray-500">
          <span>{config.label}</span>
          <span>{pct}/100</span>
        </div>
      )}
    </div>
  )
}
