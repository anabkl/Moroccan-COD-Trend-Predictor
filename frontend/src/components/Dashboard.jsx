import React, { useState } from 'react'
import { getTopProducts } from '../api/client'
import { useDashboard } from '../hooks/useDashboard'
import { useProducts } from '../hooks/useProducts'
import ScoreDistributionChart from './ScoreDistributionChart'
import ProductCard from './ProductCard'
import ProductModal from './ProductModal'
import { TrendingUp, Award, Star, BarChart2, RefreshCw, AlertCircle } from 'lucide-react'

function StatCard({ label, value, icon: Icon, colorClass = 'text-brand-DEFAULT', bgClass = 'bg-green-50' }) {
  return (
    <div className="bg-white rounded-xl shadow-md p-5 border border-gray-100 flex items-center gap-4">
      <div className={`w-12 h-12 rounded-xl ${bgClass} flex items-center justify-center flex-shrink-0`}>
        <Icon className={`w-6 h-6 ${colorClass}`} />
      </div>
      <div>
        <p className="text-gray-500 text-xs font-medium">{label}</p>
        <p className="text-2xl font-bold text-gray-900">{value ?? '–'}</p>
      </div>
    </div>
  )
}

function SkeletonStat() {
  return (
    <div className="bg-white rounded-xl shadow-md p-5 border border-gray-100 animate-pulse flex items-center gap-4">
      <div className="w-12 h-12 rounded-xl bg-gray-200" />
      <div className="flex-1">
        <div className="h-3 bg-gray-200 rounded w-1/2 mb-2" />
        <div className="h-6 bg-gray-200 rounded w-1/3" />
      </div>
    </div>
  )
}

const CATEGORY_COLORS = {
  cosmetics: '#ec4899',
  gadgets:   '#3b82f6',
  home:      '#f97316',
  fashion:   '#a855f7',
  health:    '#22c55e',
  kitchen:   '#eab308'
}

export default function Dashboard({ onNavigate }) {
  const { stats, loading: statsLoading, error: statsError, refresh } = useDashboard()
  const { products, loading: productsLoading } = useProducts()
  const [selectedProduct, setSelectedProduct] = useState(null)

  const topProducts = [...products]
    .sort((a, b) => (b.trend_score || 0) - (a.trend_score || 0))
    .slice(0, 5)

  // Category breakdown
  const categoryCounts = products.reduce((acc, p) => {
    const cat = (p.category || 'other').toLowerCase()
    acc[cat] = (acc[cat] || 0) + 1
    return acc
  }, {})

  return (
    <div className="p-6 space-y-6">
      {/* Page header */}
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-gray-900">Dashboard</h2>
          <p className="text-gray-500 text-sm mt-1">Overview of your Moroccan COD market analysis</p>
        </div>
        <button
          onClick={refresh}
          disabled={statsLoading}
          className="flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium text-gray-600 border border-gray-200 hover:bg-gray-50 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${statsLoading ? 'animate-spin' : ''}`} />
          Refresh
        </button>
      </div>

      {/* Error */}
      {statsError && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 flex items-center gap-3 text-red-700 text-sm">
          <AlertCircle className="w-5 h-5 flex-shrink-0" />
          {statsError}
        </div>
      )}

      {/* Stats cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-4">
        {statsLoading ? (
          Array.from({ length: 4 }).map((_, i) => <SkeletonStat key={i} />)
        ) : (
          <>
            <StatCard
              label="Total Products"
              value={stats?.total_products ?? products.length}
              icon={BarChart2}
              colorClass="text-blue-600"
              bgClass="bg-blue-50"
            />
            <StatCard
              label="Winning Products"
              value={stats?.winning_products ?? products.filter(p => (p.trend_score || 0) >= 80).length}
              icon={Award}
              colorClass="text-green-600"
              bgClass="bg-green-50"
            />
            <StatCard
              label="Promising"
              value={stats?.promising_products ?? products.filter(p => (p.trend_score || 0) >= 60 && (p.trend_score || 0) < 80).length}
              icon={Star}
              colorClass="text-yellow-600"
              bgClass="bg-yellow-50"
            />
            <StatCard
              label="Avg Trend Score"
              value={
                stats?.avg_trend_score != null
                  ? Math.round(stats.avg_trend_score)
                  : products.length > 0
                    ? Math.round(products.reduce((s, p) => s + (p.trend_score || 0), 0) / products.length)
                    : '–'
              }
              icon={TrendingUp}
              colorClass="text-brand-DEFAULT"
              bgClass="bg-green-50"
            />
          </>
        )}
      </div>

      {/* Charts + Category breakdown */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-5">
        <div className="lg:col-span-2">
          <ScoreDistributionChart products={products} />
        </div>
        <div className="bg-white rounded-xl shadow-md p-6 border border-gray-100">
          <h3 className="text-base font-semibold text-gray-800 mb-4">Category Breakdown</h3>
          {productsLoading ? (
            <div className="space-y-3">
              {Array.from({ length: 5 }).map((_, i) => (
                <div key={i} className="animate-pulse flex items-center gap-3">
                  <div className="w-3 h-3 rounded-full bg-gray-200" />
                  <div className="h-3 bg-gray-200 rounded flex-1" />
                  <div className="h-3 bg-gray-200 rounded w-6" />
                </div>
              ))}
            </div>
          ) : Object.keys(categoryCounts).length === 0 ? (
            <p className="text-gray-400 text-sm">No data available</p>
          ) : (
            <div className="space-y-3">
              {Object.entries(categoryCounts)
                .sort(([, a], [, b]) => b - a)
                .map(([cat, count]) => {
                  const pct = Math.round((count / products.length) * 100)
                  const color = CATEGORY_COLORS[cat] || '#94a3b8'
                  return (
                    <div key={cat}>
                      <div className="flex justify-between text-xs mb-1">
                        <span className="capitalize text-gray-600 font-medium">{cat}</span>
                        <span className="text-gray-500">{count} ({pct}%)</span>
                      </div>
                      <div className="w-full bg-gray-100 rounded-full h-1.5">
                        <div
                          className="h-1.5 rounded-full transition-all duration-700"
                          style={{ width: `${pct}%`, backgroundColor: color }}
                        />
                      </div>
                    </div>
                  )
                })}
            </div>
          )}
        </div>
      </div>

      {/* Top products */}
      <div>
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-base font-semibold text-gray-800">🏆 Top Products</h3>
          <button
            onClick={() => onNavigate && onNavigate('products')}
            className="text-sm text-brand-DEFAULT hover:text-brand-light font-medium transition-colors"
          >
            View all →
          </button>
        </div>
        {productsLoading ? (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {Array.from({ length: 5 }).map((_, i) => (
              <div key={i} className="bg-white rounded-xl shadow-md p-5 border border-gray-100 animate-pulse h-52" />
            ))}
          </div>
        ) : topProducts.length === 0 ? (
          <p className="text-gray-400 text-sm">No products available</p>
        ) : (
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-5 gap-4">
            {topProducts.map((p, i) => (
              <ProductCard key={p.id || p._id || i} product={p} onViewDetails={setSelectedProduct} />
            ))}
          </div>
        )}
      </div>

      {/* Modal */}
      {selectedProduct && (
        <ProductModal product={selectedProduct} onClose={() => setSelectedProduct(null)} />
      )}
    </div>
  )
}
