'use client'
import { useState, useEffect } from 'react'
import { Zone } from '../zones/mapping'

type Props = {
  zone: Zone | null
  onClose: () => void
}

export default function ZoneDetailsPanel({ zone, onClose }: Props) {
  const [showHistory, setShowHistory] = useState(false)

  useEffect(() => {
    setShowHistory(false)
  }, [zone?.id])

  if (!zone) return (
    <div className="flex items-center justify-center h-full
                    text-gray-500 text-sm px-6 text-center">
      📍 Click any pin on the aircraft to view zone details
    </div>
  )

  return (
    <div className="p-5 space-y-5">

      {/* Header */}
      <div className="flex justify-between items-start">
        <div>
          <p className="text-gray-400 text-xs">Zone ID</p>
          <p className="text-white font-mono font-bold text-lg">{zone.id}</p>
        </div>
        <button onClick={onClose}
          className="text-gray-500 hover:text-white text-xl">✕</button>
      </div>

      <div>
        <p className="text-gray-400 text-xs">Zone Name</p>
        <p className="text-white font-semibold">{zone.name}</p>
      </div>

      {/* Status */}
      <div>
        <p className="text-gray-400 text-xs mb-1">Status</p>
        <span className={`px-3 py-1 rounded-full text-white text-xs font-bold ${
          zone.status === 'critical' ? 'bg-red-600' :
          zone.status === 'warning'  ? 'bg-yellow-500' :
          'bg-green-600'
        }`}>
          {zone.status.toUpperCase()}
        </span>
      </div>

      {/* Details */}
      <div className="space-y-2 text-sm">
        <div className="flex justify-between border-b border-gray-800 pb-2">
          <span className="text-gray-400">Last Inspection</span>
          <span className="text-white">{zone.history[0]?.date}</span>
        </div>
        <div className="flex justify-between border-b border-gray-800 pb-2">
          <span className="text-gray-400">Defect Found</span>
          <span className={zone.history[0]?.defect ? 'text-red-400' : 'text-green-400'}>
            {zone.history[0]?.defect ? zone.history[0]?.defectType : 'None'}
          </span>
        </div>
        <div className="flex justify-between border-b border-gray-800 pb-2">
          <span className="text-gray-400">Aircraft</span>
          <span className="text-white">Boeing 737-800</span>
        </div>
      </div>

      {/* Inspection History — collapsible */}
      <div>
        <button
          onClick={() => setShowHistory(!showHistory)}
          className="flex items-center justify-between w-full
                     text-gray-300 text-sm font-bold mb-3
                     hover:text-white transition-colors"
        >
          <span>Inspection History</span>
          <span className="text-base">{showHistory ? '▲' : '▼'}</span>
        </button>

        {showHistory && (
          <div className="space-y-2">
            {zone.history.map((entry, i) => (
              <div key={i} className="flex justify-between text-sm
                                      bg-gray-800 px-4 py-3 rounded-md
                                      border border-gray-700">
                <span className="text-gray-200 font-medium">{entry.date}</span>
                <span className={`font-semibold ${entry.defect ? 'text-red-400' : 'text-green-400'}`}>
                  {entry.defect
                    ? `Defect Found${entry.defectType ? ' — ' + entry.defectType : ''}`
                    : 'Clear'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}