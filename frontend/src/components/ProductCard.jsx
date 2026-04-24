import React from 'react'
import TrendScoreBar from './TrendScoreBar'
import { Eye } from 'lucide-react'

const CATEGORY_STYLES = {
  cosmetics: 'bg-pink-100 text-pink-700',
  gadgets:   'bg-blue-100 text-blue-700',
  home:      'bg-orange-100 text-orange-700',
  fashion:   'bg-purple-100 text-purple-700',
  health:    'bg-green-100 text-green-700',
  kitchen:   'bg-yellow-100 text-yellow-700'
}

const RECOMMENDATION_CONFIG = {
  Winning:   { emoji: '🏆', cls: 'bg-green-100 text-green-800 border-green-200' },
  Promising: { emoji: '⭐', cls: 'bg-blue-100 text-blue-800 border-blue-200' },
  Watchlist: { emoji: '👀', cls: 'bg-yellow-100 text-yellow-800 border-yellow-200' },
  Avoid:     { emoji: '❌', cls: 'bg-red-100 text-red-800 border-red-200' }
}

function getCategoryStyle(category) {
  const key = (category || '').toLowerCase()
  return CATEGORY_STYLES[key] || 'bg-gray-100 text-gray-700'
}

function getRecommendationConfig(rec) {
  const key = Object.keys(RECOMMENDATION_CONFIG).find(
    (k) => (rec || '').toLowerCase().includes(k.toLowerCase())
  )
  return RECOMMENDATION_CONFIG[key] || { emoji: '📦', cls: 'bg-gray-100 text-gray-700 border-gray-200' }
}

export default function ProductCard({ product, onViewDetails }) {
  const {
    name = 'Unknown Product',
    category = 'general',
    trend_score = 0,
    recommendation = 'Watchlist',
    purchase_intent_score = 0,
    estimated_profit_margin = 0
  } = product || {}

  const recConfig = getRecommendationConfig(recommendation)

  return (
    <div className="bg-white rounded-xl shadow-md hover:shadow-lg transition-shadow duration-200 p-5 flex flex-col gap-4 border border-gray-100">
      {/* Header */}
      <div className="flex items-start justify-between gap-2">
        <h3 className="font-semibold text-gray-900 text-sm leading-snug line-clamp-2 flex-1">{name}</h3>
        <span className={`text-xs font-medium px-2 py-1 rounded-full flex-shrink-0 ${getCategoryStyle(category)}`}>
          {category}
        </span>
      </div>

      {/* Trend Score */}
      <div>
        <div className="flex justify-between items-center mb-1">
          <span className="text-xs text-gray-500 font-medium">Trend Score</span>
          <span className="text-sm font-bold text-gray-800">{Math.round(trend_score)}</span>
        </div>
        <TrendScoreBar score={trend_score} height="h-2.5" />
      </div>

      {/* Recommendation badge */}
      <div className="flex items-center gap-2">
        <span className={`inline-flex items-center gap-1 text-xs font-semibold px-3 py-1 rounded-full border ${recConfig.cls}`}>
          {recConfig.emoji} {recommendation}
        </span>
      </div>

      {/* Key metrics */}
      <div className="grid grid-cols-2 gap-2 text-xs">
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-gray-400 mb-0.5">Intent Score</p>
          <p className="font-bold text-gray-800">{(purchase_intent_score * 100).toFixed(0)}%</p>
        </div>
        <div className="bg-gray-50 rounded-lg p-2">
          <p className="text-gray-400 mb-0.5">Profit Margin</p>
          <p className="font-bold text-gray-800">{(estimated_profit_margin * 100).toFixed(0)}%</p>
        </div>
      </div>

      {/* Action */}
      <button
        onClick={() => onViewDetails && onViewDetails(product)}
        className="mt-auto flex items-center justify-center gap-2 w-full py-2 px-4 rounded-lg bg-brand-DEFAULT hover:bg-brand-light text-white text-sm font-medium transition-colors duration-200"
      >
        <Eye className="w-4 h-4" />
        View Details
      </button>
    </div>
  )
}
