import React, { useState } from 'react'
import { analyzeComment } from '../api/client'
import { MessageSquare, Loader2, Zap, AlertCircle } from 'lucide-react'
import TrendScoreBar from './TrendScoreBar'

const SAMPLE_COMMENTS = [
  { label: 'Darija (high intent)', text: 'Bghit nchri had product, fin kayn? Chhalt?', lang: 'Darija' },
  { label: 'French (medium)', text: 'Je veux commander ce produit, c\'est combien le prix?', lang: 'French' },
  { label: 'Arabic (curious)', text: 'هذا المنتج مزيان؟ واش ينفع؟', lang: 'Arabic' },
  { label: 'Darija (low intent)', text: 'Machi mhemm, ghir katshuf', lang: 'Darija' }
]

const INTENT_LEVELS = [
  { min: 8, label: 'Very High Intent', cls: 'bg-green-100 text-green-800' },
  { min: 6, label: 'High Intent',      cls: 'bg-blue-100 text-blue-800' },
  { min: 4, label: 'Medium Intent',    cls: 'bg-yellow-100 text-yellow-800' },
  { min: 0, label: 'Low Intent',       cls: 'bg-red-100 text-red-800' }
]

function getIntentLevel(score) {
  return INTENT_LEVELS.find((l) => score >= l.min) || INTENT_LEVELS[3]
}

function getLanguageStyle(lang) {
  const map = {
    darija: 'bg-orange-100 text-orange-700',
    french: 'bg-blue-100 text-blue-700',
    arabic: 'bg-purple-100 text-purple-700',
    english: 'bg-gray-100 text-gray-700'
  }
  return map[(lang || '').toLowerCase()] || 'bg-gray-100 text-gray-700'
}

export default function AnalyzeView() {
  const [text, setText] = useState('')
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleAnalyze = async () => {
    if (!text.trim()) return
    setLoading(true)
    setError(null)
    setResult(null)
    try {
      const res = await analyzeComment(text.trim())
      setResult(res.data)
    } catch (err) {
      setError(err.response?.data?.detail || 'Failed to analyze comment. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  const intentScore = result?.intent_score ?? 0
  const intentScoreNormalized = Math.min(100, (intentScore / 10) * 100)
  const intentLevel = getIntentLevel(intentScore)
  const keywords = result?.matched_keywords || result?.keywords || []
  const language = result?.language || result?.detected_language || 'Unknown'

  return (
    <div className="p-6 space-y-6 max-w-3xl mx-auto">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Comment Analyzer</h2>
        <p className="text-gray-500 text-sm mt-1">
          Detect purchase intent from Darija, French, or Arabic comments
        </p>
      </div>

      {/* Input area */}
      <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 space-y-4">
        <label className="block text-sm font-semibold text-gray-700">
          Enter a customer comment
        </label>
        <textarea
          value={text}
          onChange={(e) => setText(e.target.value)}
          placeholder="e.g. Bghit nchri had product, fin kayn? واش كاين بالدار بيضاء?"
          rows={4}
          className="w-full px-4 py-3 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-brand-DEFAULT/30 focus:border-brand-DEFAULT text-sm resize-none bg-gray-50"
        />
        <button
          onClick={handleAnalyze}
          disabled={!text.trim() || loading}
          className="flex items-center gap-2 px-6 py-2.5 rounded-xl bg-brand-DEFAULT hover:bg-brand-light text-white text-sm font-semibold transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? <Loader2 className="w-4 h-4 animate-spin" /> : <Zap className="w-4 h-4" />}
          {loading ? 'Analyzing…' : 'Analyze'}
        </button>
      </div>

      {/* Sample comments */}
      <div>
        <p className="text-xs text-gray-500 font-medium mb-2 uppercase tracking-wide">Try a sample</p>
        <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
          {SAMPLE_COMMENTS.map((s) => (
            <button
              key={s.label}
              onClick={() => setText(s.text)}
              className="text-left bg-white border border-gray-200 rounded-xl p-3 hover:border-brand-DEFAULT hover:bg-green-50 transition-all duration-150 group"
            >
              <p className="text-xs font-semibold text-gray-500 mb-1 group-hover:text-brand-DEFAULT">{s.label}</p>
              <p className="text-sm text-gray-700 line-clamp-1">{s.text}</p>
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3 text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {error}
        </div>
      )}

      {/* Results */}
      {result && (
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100 space-y-5 animate-pulse-once">
          <h3 className="text-base font-semibold text-gray-800 flex items-center gap-2">
            <MessageSquare className="w-5 h-5 text-brand-DEFAULT" />
            Analysis Results
          </h3>

          {/* Score gauge */}
          <div>
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-600">Intent Score</span>
              <span className="text-xl font-black text-brand-DEFAULT">{intentScore.toFixed(1)} / 10</span>
            </div>
            <TrendScoreBar score={intentScoreNormalized} showLabel={false} height="h-4" />
          </div>

          {/* Badges */}
          <div className="flex flex-wrap gap-3">
            <div>
              <p className="text-xs text-gray-400 mb-1">Language</p>
              <span className={`text-xs font-semibold px-3 py-1 rounded-full ${getLanguageStyle(language)}`}>
                {language}
              </span>
            </div>
            <div>
              <p className="text-xs text-gray-400 mb-1">Purchase Intent</p>
              <span className={`text-xs font-semibold px-3 py-1 rounded-full ${intentLevel.cls}`}>
                {intentLevel.label}
              </span>
            </div>
          </div>

          {/* Keywords */}
          {keywords.length > 0 && (
            <div>
              <p className="text-xs text-gray-500 font-medium mb-2">Matched Intent Keywords</p>
              <div className="flex flex-wrap gap-2">
                {keywords.map((kw, i) => (
                  <span
                    key={i}
                    className="bg-green-100 text-green-800 text-xs font-medium px-2.5 py-1 rounded-lg"
                  >
                    {kw}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Raw comment preview */}
          <div className="bg-gray-50 rounded-xl p-3">
            <p className="text-xs text-gray-400 mb-1">Analyzed Text</p>
            <p className="text-sm text-gray-700">{text}</p>
          </div>
        </div>
      )}
    </div>
  )
}
