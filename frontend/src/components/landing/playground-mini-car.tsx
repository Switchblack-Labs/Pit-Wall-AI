"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { PerspectiveCamera } from "@react-three/drei";
import { useRef } from "react";
import * as THREE from "three";


function Wireframe() {
  const ref = useRef<THREE.Group>(null!);
  useFrame((s) => {
    if (ref.current) ref.current.rotation.y = s.clock.elapsedTime * 0.4;
  });
  const wf = (
    <meshBasicMaterial wireframe color="#1A1714" />
  );
  return (
    <group ref={ref}>
      <mesh position={[0, 0.18, 0]}>
        <boxGeometry args={[1.6, 0.22, 0.62]} />
        {wf}
      </mesh>
      <mesh position={[0.85, 0.16, 0]}>
        <coneGeometry args={[0.18, 0.55, 4]} />
        {wf}
      </mesh>
      <mesh position={[0.04, 0.38, 0]}>
        <sphereGeometry args={[0.18, 12, 12]} />
        {wf}
      </mesh>
      <mesh position={[-0.78, 0.46, 0]}>
        <boxGeometry args={[0.05, 0.3, 0.7]} />
        {wf}
      </mesh>
      <mesh position={[-0.7, 0.58, 0]}>
        <boxGeometry args={[0.3, 0.025, 0.78]} />
        {wf}
      </mesh>
      {[
        [0.55, 0.13, 0.38] as const,
        [0.55, 0.13, -0.38] as const,
        [-0.55, 0.13, 0.38] as const,
        [-0.55, 0.13, -0.38] as const,
      ].map((p, i) => (
        <mesh key={i} position={p} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.16, 0.16, 0.16, 16]} />
          {wf}
        </mesh>
      ))}
      {}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <ringGeometry args={[1.5, 1.55, 64]} />
        <meshBasicMaterial color="#E26C45" transparent opacity={0.7} />
      </mesh>
    </group>
  );
}

export function PlaygroundMiniCar({ className = "" }: { className?: string }) {
  return (
    <div className={className}>
      <Canvas dpr={[1, 2]} gl={{ antialias: true, alpha: true }}>
        <PerspectiveCamera makeDefault position={[2.6, 1.8, 2.8]} fov={48} />
        <ambientLight intensity={0.6} />
        <Wireframe />
      </Canvas>
    </div>
  );
}
