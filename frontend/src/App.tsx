import StormMap from "./components/StormMap";

export default function App() {
  return (
    <div className="h-screen w-screen">
      <div className="absolute z-[1000] top-2 right-2 bg-white/90 rounded shadow p-2">
        <div className="font-bold">XWeather - Theo dõi đường đi bão</div>
        <div className="text-xs text-gray-600">Bản đồ: thường và vệ tinh, track và forecast</div>
      </div>
      <StormMap />
    </div>
  );
}