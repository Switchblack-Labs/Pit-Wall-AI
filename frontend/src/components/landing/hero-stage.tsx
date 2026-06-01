"use client";
import { Canvas, useFrame, useThree } from "@react-three/fiber";
import { Environment, Float, MeshTransmissionMaterial, PerspectiveCamera } from "@react-three/drei";
import * as THREE from "three";
import { useEffect, useRef } from "react";














function CarMesh() {
  return (
    <group>
      {}
      <mesh castShadow position={[0, 0.18, 0]}>
        <boxGeometry args={[1.7, 0.22, 0.66]} />
        <meshStandardMaterial color="#E26C45" metalness={0.78} roughness={0.22} />
      </mesh>
      {}
      <mesh position={[0.92, 0.16, 0]} rotation={[0, Math.PI / 4, 0]}>
        <coneGeometry args={[0.2, 0.6, 4]} />
        <meshStandardMaterial color="#1A1714" metalness={0.5} roughness={0.4} />
      </mesh>
      {}
      <mesh position={[0.04, 0.4, 0]}>
        <sphereGeometry args={[0.2, 32, 32]} />
        <MeshTransmissionMaterial thickness={0.4} transmission={1} roughness={0.12} ior={1.45} chromaticAberration={0.04} backside />
      </mesh>
      {}
      <mesh position={[-0.82, 0.48, 0]}>
        <boxGeometry args={[0.05, 0.3, 0.74]} />
        <meshStandardMaterial color="#F2EBE0" metalness={0.6} roughness={0.3} />
      </mesh>
      {}
      <mesh position={[-0.74, 0.6, 0]}>
        <boxGeometry args={[0.32, 0.03, 0.8]} />
        <meshStandardMaterial color="#1A1714" metalness={0.6} roughness={0.3} />
      </mesh>
      {}
      {[
        [ 0.6, 0.16,  0.4] as const,
        [ 0.6, 0.16, -0.4] as const,
        [-0.6, 0.16,  0.4] as const,
        [-0.6, 0.16, -0.4] as const,
      ].map((p, i) => (
        <mesh key={i} position={p} rotation={[Math.PI / 2, 0, 0]}>
          <cylinderGeometry args={[0.17, 0.17, 0.18, 24]} />
          <meshStandardMaterial color="#0B0908" roughness={0.85} metalness={0.05} />
        </mesh>
      ))}
    </group>
  );
}

function Stage() {
  
  
  
  return (
    <group rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
      <mesh>
        <ringGeometry args={[1.8, 1.82, 128]} />
        <meshBasicMaterial color="#E26C45" transparent opacity={0.55} />
      </mesh>
      <mesh position={[0, 0, 0.001]}>
        <ringGeometry args={[2.4, 2.41, 128]} />
        <meshBasicMaterial color="#F2EBE0" transparent opacity={0.10} />
      </mesh>
      <mesh position={[0, 0, 0.002]}>
        <ringGeometry args={[3.1, 3.11, 128]} />
        <meshBasicMaterial color="#F2EBE0" transparent opacity={0.05} />
      </mesh>
    </group>
  );
}

function RotatingCar() {
  const ref = useRef<THREE.Group>(null!);
  useFrame((_, delta) => {
    if (ref.current) ref.current.rotation.y += delta * 0.18;
  });
  return (
    <Float speed={1.1} rotationIntensity={0.05} floatIntensity={0.35}>
      <group ref={ref}>
        <CarMesh />
      </group>
    </Float>
  );
}

function LookAtCar() {
  const { camera } = useThree();
  useEffect(() => {
    camera.lookAt(0, 0.3, 0);
    camera.updateProjectionMatrix();
  }, [camera]);
  return null;
}

function Lights() {
  const a = useRef<THREE.PointLight>(null!);
  const b = useRef<THREE.PointLight>(null!);
  useFrame((s) => {
    const t = s.clock.elapsedTime;
    if (a.current) a.current.position.x = Math.sin(t * 0.4) * 6;
    if (b.current) b.current.position.x = Math.cos(t * 0.3) * 6;
  });
  return (
    <>
      <ambientLight intensity={0.4} />
      <directionalLight position={[6, 9, 4]} intensity={1.6} castShadow />
      <pointLight ref={a} position={[3, 4, 3]} intensity={22} color="#E26C45" distance={14} />
      <pointLight ref={b} position={[-3, 3, -3]} intensity={18} color="#7AB7C7" distance={14} />
    </>
  );
}

export function HeroStage() {
  return (
    <Canvas
      shadows
      dpr={[1, 2]}
      gl={{ antialias: true, alpha: true, powerPreference: "high-performance" }}
      style={{ background: "transparent" }}
      className="!absolute inset-0"
    >
      <PerspectiveCamera makeDefault position={[3.6, 2.1, 3.6]} fov={42} />
      <LookAtCar />
      <Lights />
      <Stage />
      <RotatingCar />
      <Environment preset="city" background={false} />
    </Canvas>
  );
}
