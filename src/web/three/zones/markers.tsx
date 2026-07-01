'use client'
import { useState } from 'react'
import { Html } from '@react-three/drei'
import { Zone } from './mapping'
import { STATUS_COLOR } from './colours'

type Props = {
  zone: Zone
  onClick: (zone: Zone) => void
  isSelected: boolean
}

export default function ZonePin({ zone, onClick, isSelected }: Props) {
  const [hovered, setHovered] = useState(false)
  const color = STATUS_COLOR[zone.status]

  return (
    <group
      position={zone.position}
      onClick={() => onClick(zone)}
      onPointerOver={() => setHovered(true)}
      onPointerOut={() => setHovered(false)}
    >
      {/* PIN STICK */}
      <mesh position={[0, -0.04, 0]}>
        <cylinderGeometry args={[0.003, 0.003, 0.09, 8]} />
        <meshStandardMaterial color={color} />
      </mesh>

      {/* PIN HEAD */}
      <mesh
        position={[0, 0.0, 0]}
        scale={hovered || isSelected ? 1.2 : 1}
      >
        <sphereGeometry args={[0.025, 16, 16]} />
        <meshStandardMaterial
          color={color}
          emissive={color}
          emissiveIntensity={isSelected ? 1.2 : 0.4}
        />
      </mesh>

      {/* TOOLTIP */}
      {hovered && (
        <Html distanceFactor={5}>
          <div style={{
            background: '#111827',
            color: 'white',
            padding: '5px 10px',
            borderRadius: '6px',
            fontSize: '11px',
            whiteSpace: 'nowrap',
            border: '1px solid #374151',
            pointerEvents: 'none'
          }}>
            📍 {zone.id} — {zone.name}
          </div>
        </Html>
      )}
    </group>
  )
}