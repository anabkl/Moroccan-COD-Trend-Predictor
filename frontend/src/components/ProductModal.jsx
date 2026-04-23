import React, { useEffect, useState } from 'react'
import { X } from 'lucide-react'
import TrendScoreBar from './TrendScoreBar'
import { getProduct } from '../api/client'

const METRICS = [
  { key: 'intent_score',      label: 'Purchase Intent',   max: 10 },
  { key: 'competition_score', label: 'Low Competition',   max: 10 },
  { key: 'profit_margin',     label: 'Profit Margin',     max: 100 },
  { key: 'social_buzz_score', label: 'Social Buzz',       max: 10 },
  { key: 'delivery_score',    label: 'Delivery Ease',     max: 10 }
]

function MetricBar({ label, value, max }) {
  const pct = Math.min(100, ((value || 0) / max) * 100)
  return (
    <div>
      <div className="flex justify-between text-xs mb-1">
        <span className="text-gray-600 font-medium">{label}</span>
        <span className="text-gray-800 font-bold">{value ?? 'N/A'}</span>
      </div>
      <div className="w-full bg-gray-200 rounded-full h-2">
        <div
          className="bg-brand-DEFAULT h-2 rounded-full transition-all duration-700"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

export default function ProductModal({ product, onClose }) {
  const [details, setDetails] = useState(product)
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    if (!product) return
    const id = product.id || product._id
    if (!id) return
    setLoading(true)
    getProduct(id)
      .then((res) => setDetails(res.data))
      .catch(() => setDetails(product))
      .finally(() => setLoading(false))
  }, [product?.id, product?._id])

  useEffect(() => {
    const handler = (e) => { if (e.key === 'Escape') onClose() }
    window.addEventListener('keydown', handler)
    return () => window.removeEventListener('keydown', handler)
  }, [onClose])

  if (!product) return null

  const p = details || product
  const comments = p.top_comments || []
  const explanation = p.ai_explanation || {}

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 p-4"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
        {/* Header */}
        <div className="flex items-start justify-between p-6 border-b border-gray-100">
          <div className="flex-1 pr-4">
            <h2 className="text-lg font-bold text-gray-900">{p.name}</h2>
            <p className="text-sm text-gray-500 mt-0.5">{p.category}</p>
          </div>
          <div className="flex items-center gap-3">
            <div className="text-right">
              <p className="text-2xl font-black text-brand-DEFAULT">{Math.round(p.trend_score || 0)}</p>
              <p className="text-xs text-gray-400">Trend Score</p>
            </div>
            <button
              onClick={onClose}
              className="text-gray-400 hover:text-gray-600 transition-colors p-1 rounded-lg hover:bg-gray-100"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-40 text-gray-400 text-sm">Loading details…</div>
        ) : (
          <div className="p-6 space-y-6">
            {/* Score bar */}
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-2">Overall Trend Score</p>
              <TrendScoreBar score={p.trend_score || 0} showLabel height="h-3" />
            </div>

            {/* Metrics grid */}
            <div>
              <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Scoring Factors</p>
              <div className="space-y-3">
                {METRICS.map(({ key, label, max }) => (
                  <MetricBar key={key} label={label} value={p[key]} max={max} />
                ))}
              </div>
            </div>

            {/* AI Explanation */}
            {(explanation.why_recommended || explanation.trend_reason) && (
              <div className="bg-green-50 rounded-xl p-4 space-y-2">
                <p className="text-xs font-semibold text-green-800 uppercase tracking-wide mb-1">AI Explanation</p>
                {explanation.why_recommended && (
                  <p className="text-sm text-green-900">
                    <span className="font-semibold">Why Recommended: </span>{explanation.why_recommended}
                  </p>
                )}
                {explanation.trend_reason && (
                  <p className="text-sm text-green-800">
                    <span className="font-semibold">Trend: </span>{explanation.trend_reason}
                  </p>
                )}
                {explanation.competition_reason && (
                  <p className="text-sm text-green-800">
                    <span className="font-semibold">Competition: </span>{explanation.competition_reason}
                  </p>
                )}
                {explanation.profit_reason && (
                  <p className="text-sm text-green-800">
                    <span className="font-semibold">Profit: </span>{explanation.profit_reason}
                  </p>
                )}
              </div>
            )}

            {/* Top comments */}
            {comments.length > 0 && (
              <div>
                <p className="text-xs font-semibold text-gray-500 uppercase tracking-wide mb-3">Top Comments</p>
                <div className="space-y-2">
                  {comments.map((c, i) => (
                    <div key={i} className="bg-gray-50 rounded-lg p-3 flex items-start gap-3">
                      <div className="flex-1">
                        <p className="text-sm text-gray-800">{c.text || c.comment || c}</p>
                      </div>
                      {c.intent_score != null && (
                        <span className="text-xs font-bold text-brand-DEFAULT flex-shrink-0">
                          {Math.round(c.intent_score * 10) / 10}
                        </span>
                      )}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  )
}
