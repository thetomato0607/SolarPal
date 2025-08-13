import { useMemo } from "react";
import { Float } from "@react-three/drei";
import * as THREE from "three";

// Simple floating cloud puffs
function Clouds({ cloudiness }) {
  const count = Math.min(5, Math.ceil(cloudiness / 20));
  const clouds = useMemo(() => {
    return new Array(count).fill().map((_, i) => ({
      pos: [
        Math.random() * 6 - 3,
        Math.random() * 2 + 2,
        Math.random() * 6 - 3
      ],
      scale: Math.random() * 0.8 + 0.8
    }));
  }, [count]);

  return clouds.map((c, i) => (
    <Float key={i} speed={0.5} rotationIntensity={0.1} floatIntensity={0.2}>
      <mesh position={c.pos} scale={c.scale}>
        <sphereGeometry args={[0.8, 16, 16]} />
        <meshStandardMaterial color="#ffffff" opacity={0.9} transparent />
      </mesh>
    </Float>
  ));
}

// Falling rain lines
function Rain() {
  const drops = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    const count = 500;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 1] = Math.random() * 5;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
    }
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return geo;
  }, []);

  return (
    <points geometry={drops}>
      <pointsMaterial color="#88ccee" size={0.05} transparent opacity={0.8} />
    </points>
  );
}

// Falling snow particles
function Snow() {
  const flakes = useMemo(() => {
    const geo = new THREE.BufferGeometry();
    const count = 400;
    const positions = new Float32Array(count * 3);
    for (let i = 0; i < count; i++) {
      positions[i * 3] = (Math.random() - 0.5) * 10;
      positions[i * 3 + 1] = Math.random() * 5;
      positions[i * 3 + 2] = (Math.random() - 0.5) * 10;
    }
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
    return geo;
  }, []);

  return (
    <points geometry={flakes}>
      <pointsMaterial color="#ffffff" size={0.08} transparent opacity={0.9} />
    </points>
  );
}

export default function WeatherEffects({ weather }) {
  if (!weather) return null;

  const main = weather.weather?.[0]?.main || "";
  const cloudiness = weather.clouds?.all || 0;

  if (main === "Rain") return <Rain />;
  if (main === "Snow") return <Snow />;
  if (cloudiness > 30) return <Clouds cloudiness={cloudiness} />;
  return null;
}
