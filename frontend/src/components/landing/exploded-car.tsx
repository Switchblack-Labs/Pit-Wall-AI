"use client";
import { Canvas, useFrame } from "@react-three/fiber";
import { PerspectiveCamera, Environment } from "@react-three/drei";
import * as THREE from "three";
import { useEffect, useRef } from "react";

















type PartDef = {
  shape: "box" | "cone" | "sphere" | "cyl";
  args: number[];
  
  pos: [number, number, number];
  
  dir: [number, number, number];
  color: string;
  rot?: [number, number, number];
};

const PARTS: PartDef[] = [
  
  { shape: "box",    args: [1.6, 0.22, 0.62], pos: [0, 0.18, 0],     dir: [0, 0.4, 0],   color: "#E26C45" },
  
  { shape: "cone",   args: [0.18, 0.55, 4],   pos: [0.85, 0.16, 0],  dir: [1.7, 0.15, 0], color: "#1A1714" },
  
  { shape: "sphere", args: [0.18, 24, 24],    pos: [0.04, 0.38, 0],  dir: [0, 1.4, 0],   color: "#7AB7C7" },
  
  { shape: "box",    args: [0.05, 0.3, 0.7],  pos: [-0.78, 0.46, 0], dir: [-1.6, 0.5, 0], color: "#F2EBE0" },
  
  { shape: "box",    args: [0.3, 0.025, 0.78],pos: [-0.7, 0.58, 0],  dir: [-1.6, 0.9, 0], color: "#1A1714" },
  
  { shape: "cyl", args: [0.16, 0.16, 0.16, 20], pos: [ 0.55, 0.13,  0.38], dir: [ 0.9, -0.3,  1.4], color: "#0B0908", rot: [Math.PI/2, 0, 0] },
  { shape: "cyl", args: [0.16, 0.16, 0.16, 20], pos: [ 0.55, 0.13, -0.38], dir: [ 0.9, -0.3, -1.4], color: "#0B0908", rot: [Math.PI/2, 0, 0] },
  { shape: "cyl", args: [-0.55, 0.13, 0.38, 20].slice(0,4), pos: [-0.55, 0.13,  0.38], dir: [-0.9, -0.3,  1.4], color: "#0B0908", rot: [Math.PI/2, 0, 0] },
  { shape: "cyl", args: [0.16, 0.16, 0.16, 20], pos: [-0.55, 0.13, -0.38], dir: [-0.9, -0.3, -1.4], color: "#0B0908", rot: [Math.PI/2, 0, 0] },
];

function Geo({ shape, args }: { shape: PartDef["shape"]; args: number[] }) {
  if (shape === "box")    return <boxGeometry args={args as [number, number, number]} />;
  if (shape === "cone")   return <coneGeometry args={args as [number, number, number]} />;
  if (shape === "sphere") return <sphereGeometry args={args as [number, number, number]} />;
  return <cylinderGeometry args={args as [number, number, number, number]} />;
}

function ExplodedPart({
  part,
  progressRef,
}: {
  part: PartDef;
  progressRef: React.MutableRefObject<number>;
}) {
  const ref = useRef<THREE.Mesh>(null!);
  useFrame(() => {
    const p = progressRef.current;
    if (!ref.current) return;
    ref.current.position.set(
      part.pos[0] + part.dir[0] * p,
      part.pos[1] + part.dir[1] * p,
      part.pos[2] + part.dir[2] * p
    );
    if (part.rot) {
      ref.current.rotation.set(
        part.rot[0] + p * 0.3,
        part.rot[1] + p * 0.4,
        part.rot[2] + p * 0.25
      );
    } else {
      ref.current.rotation.set(p * 0.35, p * 0.45, p * 0.2);
    }
  });
  return (
    <mesh ref={ref}>
      <Geo shape={part.shape} args={part.args} />
      <meshStandardMaterial color={part.color} metalness={0.55} roughness={0.4} />
    </mesh>
  );
}

function Scene({ progressRef }: { progressRef: React.MutableRefObject<number> }) {
  return (
    <>
      <ambientLight intensity={0.9} />
      <directionalLight position={[4, 6, 3]} intensity={1.4} />
      <directionalLight position={[-4, 4, -2]} intensity={0.5} color="#E26C45" />
      <group>
        {PARTS.map((p, i) => (
          <ExplodedPart key={i} part={p} progressRef={progressRef} />
        ))}
      </group>
      <Environment preset="apartment" />
    </>
  );
}

export type ExplodedCarHandle = {
  setProgress: (p: number) => void;
};

export function ExplodedCar({
  className = "",
  initialProgress = 0,
}: {
  className?: string;
  initialProgress?: number;
}) {
  const progressRef = useRef(initialProgress);
  const apiRef = useRef<ExplodedCarHandle>({
    setProgress: (p: number) => { progressRef.current = Math.max(0, Math.min(1, p)); },
  });

  useEffect(() => {
    (window as any).__exploded = apiRef.current;
  }, []);

  return (
    <div className={className}>
      <Canvas dpr={[1, 2]} gl={{ antialias: true, alpha: true }}>
        <PerspectiveCamera makeDefault position={[3.2, 1.8, 3.2]} fov={45} />
        <Scene progressRef={progressRef} />
      </Canvas>
    </div>
  );
}
