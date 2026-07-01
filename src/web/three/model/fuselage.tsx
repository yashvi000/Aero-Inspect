'use client'
import { useGLTF } from '@react-three/drei'

export default function FuselageModel() {
  const { scene } = useGLTF('/models/fuselage.glb')
  return (
    <primitive object={scene} scale={2.5} />
  )
}