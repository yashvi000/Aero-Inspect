'use client'
import { Suspense } from 'react'
import { Canvas } from '@react-three/fiber'
import { Center } from '@react-three/drei'
import Lights from './lights'
import Controls from './controls'
import FuselageModel from '../model/fuselage'
import ZonePin from '../zones/markers'
import { Zone } from '../zones/mapping'

type Props = {
  zones: Zone[]
  selectedZone: Zone | null
  onZoneClick: (zone: Zone) => void
}

export default function AeroCanvas({ zones, selectedZone, onZoneClick }: Props) {
  return (
    <div className="w-full h-full relative">
      <Canvas camera={{ position: [12, 4.5, 10], fov: 11 }}>
        <Lights />
        <Suspense fallback={null}>
          <Center>
            <FuselageModel />
          </Center>
          {zones.map(zone => (
            <ZonePin
              key={zone.id}
              zone={zone}
              onClick={onZoneClick}
              isSelected={selectedZone?.id === zone.id}
            />
          ))}
        </Suspense>
        <Controls />
      </Canvas>
      <div className="absolute bottom-4 left-4 text-gray-600 text-xs">
        🖱️ Drag: Rotate | Scroll: Zoom | Right drag: Pan
      </div>
    </div>
  )
}