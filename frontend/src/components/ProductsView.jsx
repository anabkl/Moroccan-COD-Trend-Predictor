import React, { useState } from 'react'
import { Search, Filter, Package } from 'lucide-react'
import { useProducts } from '../hooks/useProducts'
import ProductCard from './ProductCard'
import ProductModal from './ProductModal'

const CATEGORIES = ['All', 'Cosmetics', 'Gadgets', 'Home', 'Fashion', 'Health', 'Kitchen']

function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl shadow-md p-5 border border-gray-100 animate-pulse">
      <div className="h-4 bg-gray-200 rounded w-3/4 mb-3" />
      <div className="h-3 bg-gray-200 rounded w-1/2 mb-4" />
      <div className="h-2 bg-gray-200 rounded w-full mb-2" />
      <div className="h-8 bg-gray-200 rounded w-full mt-4" />
    </div>
  )
}

export default function ProductsView() {
  const [search, setSearch] = useState('')
  const [activeCategory, setActiveCategory] = useState('All')
  const [selectedProduct, setSelectedProduct] = useState(null)
  const [page, setPage] = useState(1)
  const PAGE_SIZE = 12

  const { products, loading, error } = useProducts()

  const filtered = products.filter((p) => {
    const matchSearch = search === '' || (p.name || '').toLowerCase().includes(search.toLowerCase())
    const matchCategory = activeCategory === 'All' ||
      (p.category || '').toLowerCase() === activeCategory.toLowerCase()
    return matchSearch && matchCategory
  })

  const totalPages = Math.ceil(filtered.length / PAGE_SIZE)
  const paginated = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE)

  const handleSearch = (e) => {
    setSearch(e.target.value)
    setPage(1)
  }

  const handleCategory = (cat) => {
    setActiveCategory(cat)
    setPage(1)
  }

  return (
    <div className="p-6 space-y-6">
      {/* Header */}
      <div>
        <h2 className="text-2xl font-bold text-gray-900">Products</h2>
        <p className="text-gray-500 text-sm mt-1">
          {loading ? 'Loading…' : `${filtered.length} product${filtered.length !== 1 ? 's' : ''} found`}
        </p>
      </div>

      {/* Search + filter */}
      <div className="flex flex-col sm:flex-row gap-3">
        <div className="relative flex-1">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="Search products…"
            value={search}
            onChange={handleSearch}
            className="w-full pl-9 pr-4 py-2.5 rounded-xl border border-gray-200 focus:outline-none focus:ring-2 focus:ring-brand-DEFAULT/30 focus:border-brand-DEFAULT text-sm bg-white"
          />
        </div>
        <div className="flex items-center gap-1.5 flex-wrap">
          <Filter className="w-4 h-4 text-gray-400 flex-shrink-0" />
          {CATEGORIES.map((cat) => (
            <button
              key={cat}
              onClick={() => handleCategory(cat)}
              className={`px-3 py-2 rounded-lg text-xs font-medium transition-colors duration-150
                ${activeCategory === cat
                  ? 'bg-brand-DEFAULT text-white'
                  : 'bg-white text-gray-600 border border-gray-200 hover:bg-gray-50'
                }`}
            >
              {cat}
            </button>
          ))}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 text-red-700 text-sm">
          ⚠️ {error}
        </div>
      )}

      {/* Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-5">
        {loading
          ? Array.from({ length: 8 }).map((_, i) => <SkeletonCard key={i} />)
          : paginated.map((p, i) => (
              <ProductCard key={p.id || p._id || i} product={p} onViewDetails={setSelectedProduct} />
            ))
        }
      </div>

      {/* Empty state */}
      {!loading && paginated.length === 0 && !error && (
        <div className="text-center py-16 text-gray-400">
          <Package className="w-12 h-12 mx-auto mb-3 opacity-40" />
          <p className="font-medium">No products found</p>
          <p className="text-sm mt-1">Try adjusting your search or filters</p>
        </div>
      )}

      {/* Pagination */}
      {totalPages > 1 && (
        <div className="flex items-center justify-center gap-2 pt-2">
          <button
            onClick={() => setPage((p) => Math.max(1, p - 1))}
            disabled={page === 1}
            className="px-4 py-2 rounded-lg text-sm font-medium border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
          >
            Previous
          </button>
          <span className="text-sm text-gray-600">
            Page {page} of {totalPages}
          </span>
          <button
            onClick={() => setPage((p) => Math.min(totalPages, p + 1))}
            disabled={page === totalPages}
            className="px-4 py-2 rounded-lg text-sm font-medium border border-gray-200 disabled:opacity-40 hover:bg-gray-50 transition-colors"
          >
            Next
          </button>
        </div>
      )}

      {/* Modal */}
      {selectedProduct && (
        <ProductModal product={selectedProduct} onClose={() => setSelectedProduct(null)} />
      )}
    </div>
  )
}
