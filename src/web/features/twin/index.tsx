'use client'
import { useState } from 'react'
import dynamic from 'next/dynamic'
import { ZONES } from '../../three/zones/mapping'
import type { Zone } from '../../three/zones/mapping'
import ZoneDetailsPanel from '../../three/panels/zone_details'

const AeroCanvas = dynamic(
  () => import('../../three/scene/canvas'),
  { ssr: false }
)

export default function DigitalTwinFeature() {
  const [selectedZone, setSelectedZone] = useState<Zone | null>(null)
  const [filter, setFilter] = useState('All')
  const [defectFilter, setDefectFilter] = useState('All')

  const filteredZones = ZONES.filter(z => {
    if (selectedZone) return z.id === selectedZone.id
    if (filter === 'Critical') return z.status === 'critical'
    if (filter === 'Warning')  return z.status === 'warning'
    if (filter === 'Normal')   return z.status === 'normal'
    return true
  })

  return (
    <div className="flex h-screen bg-gray-950">

      {/* Left 70% */}
      <div className="w-[70%] flex flex-col">

        {/* Top row: Defect + Variant */}
        <div className="flex items-center gap-2 px-4 py-2
                        bg-gray-900 border-b border-gray-800">
          <span className="text-gray-400 text-xs">Defect:</span>
          {['All','Crack','Corrosion','Scratch','Dent','Paint'].map(f => (
            <button key={f}
              onClick={() => setDefectFilter(f)}
              className={`px-2.5 py-1 rounded text-xs font-medium
                ${defectFilter === f
                  ? 'bg-purple-600 text-white'
                  : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                }`}>
              {f}
            </button>
          ))}
          <div className="ml-auto w-72 flex justify-center"></div>
          <select
            className="ml-auto bg-gray-800 text-white text-xs
                       px-2 py-1 rounded border border-gray-700
                       cursor-pointer w-40"
            defaultValue="737-800"
          >
            <option disabled value="737-700">B737-700 🔒</option>
            <option value="737-800">✈ B737-800 ✅</option>
            <option disabled value="737-900">B737-900 🔒</option>
            <option disabled value="737-MAX8">B737 MAX 8 🔒</option>
          </select>
        </div>

        {/* 3D model area */}
        <div className="flex-1 relative">

          {/* Severity filter — floating left */}
          <div className="absolute top-3 left-3 z-10
                          flex items-center gap-2
                          bg-gray-900/85 backdrop-blur-sm
                          px-3 py-1.5 rounded-lg border border-gray-700">
            <span className="text-gray-400 text-xs">Severity:</span>
            {['All','Critical','Warning','Normal'].map(f => (
              <button key={f}
                onClick={() => setFilter(f)}
                className={`px-2.5 py-1 rounded text-xs font-medium
                  ${filter === f
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-800 text-gray-400 hover:bg-gray-700'
                  }`}>
                {f}
              </button>
            ))}
          </div>

          {/* Zone selector — floating right */}
          <select
            className="absolute top-3 right-4 z-10
                       bg-gray-800 text-white text-xs
                       px-2 py-1.5 rounded-lg border
                       border-gray-700 cursor-pointer w-59"
            value={selectedZone?.id || ''}
            onChange={(e) => {
              const zone = ZONES.find(z => z.id === e.target.value)
              setSelectedZone(zone || null)
            }}
          >
            <option value="">Select Zone</option>
            {ZONES.map(zone => (
              <option key={zone.id} value={zone.id}>
                {zone.id} — {zone.name}
              </option>
            ))}
            <option value="others">Others</option>
          </select>

          {/* 3D canvas */}
          <AeroCanvas
            zones={filteredZones}
            selectedZone={selectedZone}
            onZoneClick={setSelectedZone}
          />

          {/* Controls hint */}
          <div className="absolute bottom-4 left-4 text-gray-600 text-xs">
            🖱️ Drag: Rotate | Scroll: Zoom | Right drag: Pan
          </div>
        </div>
      </div>

      {/* Right 30% — zone details */}
      <div className="w-[30%] bg-gray-900 border-l border-gray-800 overflow-y-auto">
        <ZoneDetailsPanel
          zone={selectedZone}
          onClose={() => setSelectedZone(null)}
        />
      </div>
    </div>
  )
}