import { useEffect, useMemo, useState } from "react";
import {
  fetchActiveStorms,
  fetchForecasts,
  fetchStorm,
  fetchStormGeoJSON,
  fetchTracks,
} from "../lib/api";
import type { ForecastPoint, Storm, TrackPoint } from "../lib/api";
import type { GeoJsonObject } from "geojson";

export default function useStormData() {
  const [storms, setStorms] = useState<Storm[]>([]);
  const [selectedStormId, setSelectedStormId] = useState<string | undefined>();
  const [stormInfo, setStormInfo] = useState<Storm | null>(null);
  const [tracks, setTracks] = useState<TrackPoint[]>([]);
  const [forecasts, setForecasts] = useState<ForecastPoint[]>([]);
  const [geojson, setGeojson] = useState<GeoJsonObject | null>(null);
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    (async () => {
      try {
        const data = await fetchActiveStorms();
        setStorms(data);
        if (data.length > 0) setSelectedStormId(data[0].storm_id);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Lỗi tải danh sách bão");
      }
    })();
  }, []);

  useEffect(() => {
    if (!selectedStormId) return;
    setLoading(true);
    setError(null);
    (async () => {
      try {
        const [s, tr, fc, gj] = await Promise.all([
          fetchStorm(selectedStormId),
          fetchTracks(selectedStormId, 5000),
          fetchForecasts(selectedStormId, 1000),
          fetchStormGeoJSON(selectedStormId).catch(() => null),
        ]);
        setStormInfo(s);
        setTracks(tr ?? []);
        setForecasts(fc ?? []);
        setGeojson(gj ?? null);
      } catch (e: unknown) {
        setError(e instanceof Error ? e.message : "Lỗi tải dữ liệu bão");
      } finally {
        setLoading(false);
      }
    })();
  }, [selectedStormId]);

  const trackLatLngs = useMemo(
    () =>
      tracks
        .filter((p) => p.lat != null && p.lon != null)
        .map((p) => [p.lat as number, p.lon as number]) as [number, number][],
    [tracks]
  );
  const forecastLatLngs = useMemo(
    () =>
      forecasts
        .filter((p) => p.lat != null && p.lon != null)
        .map((p) => [p.lat as number, p.lon as number]) as [number, number][],
    [forecasts]
  );

  return {
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
  };
}
