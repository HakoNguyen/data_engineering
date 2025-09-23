import { useEffect, useMemo, useRef, useState } from "react";
import {
  MapContainer,
  LayersControl,
  GeoJSON,
  ZoomControl,
  useMap,
} from "react-leaflet";
import L from "leaflet";
import useStormData from "../hooks/useStormData";
import BaseLayers from "./map/BaseLayers";
import TrackLayer from "./map/TrackLayer";
import ForecastLayer from "./map/ForecastLayer";
import StormMarker from "./map/StormMarker";
import WeatherLayers from "./WeatherLayers";
import "../index.css";

import markerIcon2xUrl from "leaflet/dist/images/marker-icon-2x.png?url";
import markerIconUrl from "leaflet/dist/images/marker-icon.png?url";
import markerShadowUrl from "leaflet/dist/images/marker-shadow.png?url";
L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2xUrl,
  iconUrl: markerIconUrl,
  shadowUrl: markerShadowUrl,
});

type Props = { initialCenter?: [number, number]; initialZoom?: number };

const DEFAULT_CENTER: [number, number] = [25.0, -80.0];
const DEFAULT_ZOOM = 5;

export default function StormMap({
  initialCenter = DEFAULT_CENTER,
  initialZoom = DEFAULT_ZOOM,
}: Props) {
  const OWM_KEY = import.meta.env.VITE_OWM_API_KEY as string | undefined;
  const [bannerLang, setBannerLang] = useState<"vi" | "en">("vi");
  const mapRef = useRef<L.Map | null>(null);
  const {
    storms,
    selectedStormId,
    setSelectedStormId,
    stormInfo,
    tracks,
    forecasts,
    geojson,
    loading,
    error,
    trackLatLngs,
    forecastLatLngs,
  } = useStormData();

  useEffect(() => {
    try {
      const all = [...trackLatLngs, ...forecastLatLngs];
      if (mapRef.current && all.length > 0) {
        const bounds = L.latLngBounds(
          all.map(([lat, lon]) => L.latLng(lat, lon))
        );
        mapRef.current.fitBounds(bounds.pad(0.2));
      }
    } catch (e) {
      console.error("Error fitting map bounds:", e);
    }
  }, [trackLatLngs, forecastLatLngs]);

  // Tâm bản đồ theo storm (nếu có)
  const mapCenter = useMemo<[number, number]>(() => {
    if (stormInfo?.lat != null && stormInfo?.lon != null) {
      return [stormInfo.lat as number, stormInfo.lon as number];
    }
    return initialCenter;
  }, [stormInfo, initialCenter]);

  function AutoFitBounds({ points }: { points: [number, number][] }) {
    const map = useMap();
    useEffect(() => {
      try {
        if (points.length > 0) {
          const bounds = L.latLngBounds(
            points.map(([lat, lon]) => L.latLng(lat, lon))
          );
          map.fitBounds(bounds.pad(0.2));
        }
      } catch {}
    }, [points, map]);
    return null;
  }

  return (
    <div className="w-full h-full flex flex-col">
      <div className="p-3 border-b flex items-center gap-3 bg-white">
        <div className="font-semibold">Chọn bão:</div>
        <select
          className="border rounded px-2 py-1"
          value={selectedStormId ?? ""}
          onChange={(e) => setSelectedStormId(e.target.value)}
        >
          {storms.map((s) => (
            <option key={s.storm_id} value={s.storm_id}>
              {s.name ?? s.storm_id} {s.basin ? `(${s.basin})` : ""}
            </option>
          ))}
        </select>
        {loading && <span className="text-sm text-gray-500">Đang tải…</span>}
        {error && <span className="text-sm text-red-600">{error}</span>}
      </div>

      <div className="flex-1 relative">
        <MapContainer
          center={mapCenter}
          zoom={initialZoom}
          className="w-full h-full"
          zoomControl={false}
          whenCreated={(m) => {
            mapRef.current = m as unknown as L.Map;
          }}
        >
          <AutoFitBounds points={[...trackLatLngs, ...forecastLatLngs]} />
          <ZoomControl position="bottomright" />
          <LayersControl position="topright">
            <BaseLayers />

            <LayersControl.Overlay checked name="Track & Forecast">
              <>
                <TrackLayer positions={trackLatLngs} trackPoints={tracks} />
                <ForecastLayer
                  positions={forecastLatLngs}
                  forecasts={forecasts}
                />
              </>
            </LayersControl.Overlay>

            <StormMarker storm={stormInfo ?? undefined} />

            <WeatherLayers owmKey={OWM_KEY} />

            {geojson && (
              <LayersControl.Overlay name="GeoJSON (từ backend)">
                <GeoJSON data={geojson} />
              </LayersControl.Overlay>
            )}
          </LayersControl>
        </MapContainer>
        <div
          className="absolute bottom-0 left-1/2 -translate-x-1/2 mb-2 bg-white/80 text-gray-800 text-xs md:text-sm px-3 py-1 rounded shadow cursor-pointer select-none z-[1200]"
          onClick={() => setBannerLang((prev) => (prev === "vi" ? "en" : "vi"))}
          title={
            bannerLang === "vi"
              ? "Click to switch to English"
              : "Nhấn để chuyển sang Tiếng Việt"
          }
        >
          {bannerLang === "vi"
            ? "Hoàng Sa, Trường Sa là của Việt Nam. Dù trước kia hay mãi về sau"
            : "Hoang Sa and Truong Sa belong to Vietnam. In the past and forever"}
        </div>
      </div>
    </div>
  );
}
