import { Canvas, useFrame } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import * as THREE from "three";
import { useMemo, useRef, useState, useEffect } from "react";
import WeatherEffects from "./WeatherEffects";

export default function HouseScene({ height = 400, forecast, weather }) {
  return (
    <div style={{ height, width: "100%", borderRadius: 16, overflow: "hidden" }}>
      <Canvas camera={{ position: [5, 4, 5], fov: 50 }}>
        <ambientLight intensity={0.5} />
        <directionalLight position={[5, 8, 5]} intensity={1} />
        <House />
        <GridPlane />

        {/* Weather animations */}
        {weather && <WeatherEffects weather={weather} />}

        <OrbitControls minDistance={4} maxDistance={12} maxPolarAngle={Math.PI / 2.2} />
      </Canvas>
    </div>
  );
}
/* ===== House + Grid ===== */
function GridPlane() {
  return (
    <mesh rotation={[-Math.PI/2, 0, 0]} receiveShadow>
      <planeGeometry args={[20, 20, 20, 20]} />
      <meshStandardMaterial color="#ffe9cc" wireframe />
    </mesh>
  );
}

function House() {
  return (
    <group>
      <mesh position={[0, 1, 0]} castShadow>
        <boxGeometry args={[2, 2, 2]} />
        <meshStandardMaterial color="#ffffff" />
      </mesh>
      <mesh position={[0, 2.5, 0]} castShadow>
        <coneGeometry args={[1.6, 1, 4]} />
        <meshStandardMaterial color="#ff7a59" />
      </mesh>
      <mesh position={[0, 0.3, 1.01]} castShadow>
        <boxGeometry args={[0.6, 1, 0.05]} />
        <meshStandardMaterial color="#8b5a2b" />
      </mesh>
      <mesh position={[1.01, 1.3, 0]} castShadow>
        <boxGeometry args={[0.05, 0.6, 0.6]} />
        <meshStandardMaterial color="#cfefff" />
      </mesh>
      <mesh position={[-1.01, 1.3, 0]} castShadow>
        <boxGeometry args={[0.05, 0.6, 0.6]} />
        <meshStandardMaterial color="#cfefff" />
      </mesh>
    </group>
  );
}

/* ===== Clouds (density from cloud cover) ===== */
function Clouds({ forecast }) {
  const hour = useForecastHour(forecast);
  const cloud = clamp01(hour?.cloud ?? 0.2); // 0..1

  const count = Math.round(6 + cloud * 10); // more clouds → more sprites
  const clouds = useMemo(() => [...Array(count)].map((_, i) => ({
    x: -8 + Math.random() * 16,
    y: 3 + Math.random() * 3,
    z: -6 + Math.random() * 12,
    s: 0.8 + Math.random() * 1.6,
    speed: 0.002 + Math.random() * 0.004
  })), [count]);

  const group = useRef();
  useFrame((_, dt) => {
    if (!group.current) return;
    group.current.children.forEach((m, i) => {
      m.position.x += clouds[i].speed;
      if (m.position.x > 10) m.position.x = -10;
    });
  });

  return (
    <group ref={group}>
      {clouds.map((c, i) => (
        <mesh key={i} position={[c.x, c.y, c.z]}>
          <sphereGeometry args={[c.s, 16, 16]} />
          <meshStandardMaterial color="#ffffff" transparent opacity={0.8} />
        </mesh>
      ))}
    </group>
  );
}

/* ===== Rain (intensity from rain_mm) ===== */
function Rain({ forecast }) {
  const hour = useForecastHour(forecast);
  const intensity = Math.min(hour?.rain_mm ?? 0, 6) / 6; // 0..1
  const drops = Math.round(intensity * 300); // scale
  const geo = useMemo(() => new THREE.BufferGeometry(), []);
  const mat = useMemo(
    () => new THREE.PointsMaterial({ color: 0x2ea3f2, size: 0.05, transparent: true, opacity: 0.8 }),
    []
  );
  const positions = useMemo(() => {
    const a = new Float32Array(drops * 3);
    for (let i = 0; i < drops; i++) {
      a[i*3+0] = -6 + Math.random() * 12;
      a[i*3+1] = 6 + Math.random() * 6;
      a[i*3+2] = -6 + Math.random() * 12;
    }
    return a;
  }, [drops]);

  useEffect(() => {
    geo.setAttribute("position", new THREE.BufferAttribute(positions, 3));
  }, [positions]);

  const points = useRef();
  useFrame((_, dt) => {
    if (!points.current) return;
    const pos = points.current.geometry.attributes.position;
    for (let i = 0; i < pos.count; i++) {
      let y = pos.getY(i) - (8 * dt);
      if (y < 0) y = 8 + Math.random() * 4;
      pos.setY(i, y);
    }
    pos.needsUpdate = true;
  });

  if (!drops) return null;
  return <points ref={points} geometry={geo} material={mat} />;
}

/* ===== Wind flag (sway from wind_ms) ===== */
function WindFlag({ forecast }) {
  const hour = useForecastHour(forecast);
  const wind = Math.min(hour?.wind_ms ?? 0, 12) / 12; // 0..1
  const ref = useRef();
  useFrame((state) => {
    if (!ref.current) return;
    ref.current.rotation.z = Math.sin(state.clock.elapsedTime * (1.5 + wind*2)) * (0.05 + wind*0.25);
  });
  return (
    <mesh ref={ref} position={[1.2, 2.8, -1]}>
      <boxGeometry args={[0.02, 0.8, 0.02]} />
      <meshStandardMaterial color="#444" />
      <mesh position={[0.25, 0, 0]}>
        <boxGeometry args={[0.5, 0.2, 0.01]} />
        <meshStandardMaterial color="#2ea3f2" />
      </mesh>
    </mesh>
  );
}

/* ===== Helpers ===== */
function useForecastHour(forecast){
  const [i, setI] = useState(0);
  const arr = forecast?.hourly ?? [];
  useEffect(() => {
    if (!arr.length) return;
    let idx = 0;
    const id = setInterval(() => { idx = (idx+1) % arr.length; setI(idx); }, 1500);
    return () => clearInterval(id);
  }, [arr.length]);
  return arr[i];
}
function clamp01(x){ return Math.max(0, Math.min(1, Number(x)||0)); }
