import React, { useState } from 'react'
import Sidebar from './components/Sidebar'
import Dashboard from './components/Dashboard'
import ProductsView from './components/ProductsView'
import AnalyzeView from './components/AnalyzeView'

export default function App() {
  const [activeView, setActiveView] = useState('dashboard')

  const renderView = () => {
    switch (activeView) {
      case 'dashboard': return <Dashboard onNavigate={setActiveView} />
      case 'products':  return <ProductsView />
      case 'analyze':   return <AnalyzeView />
      default:          return <Dashboard onNavigate={setActiveView} />
    }
  }

  return (
    <div className="flex min-h-screen bg-gray-50">
      <Sidebar activeView={activeView} onNavigate={setActiveView} />
      <main className="flex-1 overflow-auto">
        {renderView()}
      </main>
    </div>
  )
}
