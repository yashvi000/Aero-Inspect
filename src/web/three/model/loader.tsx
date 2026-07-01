'use client'

export default function ModelLoader() {
  return (
    <mesh>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="#1d4ed8" wireframe={true} />
    </mesh>
  )
}