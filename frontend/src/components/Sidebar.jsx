import React from 'react'
import { LayoutDashboard, Package, MessageSquare, Zap } from 'lucide-react'

const NAV_ITEMS = [
  { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard },
  { id: 'products',  label: 'Products',  icon: Package },
  { id: 'analyze',   label: 'Analyze Comment', icon: MessageSquare }
]

export default function Sidebar({ activeView, onNavigate }) {
  return (
    <aside className="w-64 min-h-screen bg-brand-dark flex flex-col shadow-xl">
      {/* Logo */}
      <div className="px-6 py-6 border-b border-green-800">
        <div className="flex items-center gap-3">
          <div className="w-9 h-9 rounded-lg bg-brand-light flex items-center justify-center">
            <Zap className="w-5 h-5 text-white" />
          </div>
          <div>
            <h1 className="text-white font-bold text-lg leading-tight">SoukAI</h1>
            <p className="text-green-300 text-xs">Moroccan COD Analyzer</p>
          </div>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 px-4 py-6 space-y-1">
        {NAV_ITEMS.map(({ id, label, icon: Icon }) => {
          const active = activeView === id
          return (
            <button
              key={id}
              onClick={() => onNavigate(id)}
              className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-sm font-medium transition-all duration-200
                ${active
                  ? 'bg-brand-light text-white shadow-md'
                  : 'text-green-200 hover:bg-green-800 hover:text-white'
                }`}
            >
              <Icon className="w-5 h-5 flex-shrink-0" />
              {label}
            </button>
          )
        })}
      </nav>

      {/* Footer */}
      <div className="px-6 py-4 border-t border-green-800">
        <p className="text-green-400 text-xs">SoukAI v1.0.0</p>
        <p className="text-green-600 text-xs mt-0.5">Powered by AI 🤖</p>
      </div>
    </aside>
  )
}
