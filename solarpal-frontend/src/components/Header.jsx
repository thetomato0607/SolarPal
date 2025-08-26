import GhostButton from "./ui/GhostButton";

export default function Header({ onReset }) {
  return (
    <header className="flex items-center justify-between w-full max-w-screen-lg mx-auto px-4 py-3">
      <div className="font-extrabold tracking-wide text-xl sm:text-2xl">🌤️ SolarPal</div>
      <GhostButton onClick={onReset} className="text-sm sm:text-base">Reset</GhostButton>
    </header>
  );
}
