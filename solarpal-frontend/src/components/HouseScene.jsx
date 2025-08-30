import { Canvas } from "@react-three/fiber";
import { OrbitControls } from "@react-three/drei";
import WeatherEffects from "./WeatherEffects";

export default function HouseScene({ height = 400, weather }) {
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
