const API_BASE = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

// GeoJSON types (tối thiểu) để tránh dùng any
export type LineStringFeature = {
  type: "Feature";
  properties: Record<string, unknown>;
  geometry: {
    type: "LineString";
    coordinates: [number, number][];
  };
};

export type FeatureCollection = {
  type: "FeatureCollection";
  features: LineStringFeature[];
};

export type Storm = {
  storm_id: string;
  name?: string;
  basin?: string;
  event?: string;
  storm_type?: string;
  storm_cat?: string;
  lon?: number | null;
  lat?: number | null;
};

export type TrackPoint = {
  id?: number;
  storm_id: string;
  time?: string;
  lon: number;
  lat: number;
  wind_speed?: number | null;
  pressure?: number | null;
};

export type ForecastPoint = {
  id?: number;
  storm_id: string;
  forecast_time?: string;
  lon: number;
  lat: number;
  wind_speed?: number | null;
  pressure?: number | null;
  storm_cat?: string | null;
  storm_type?: string | null;
  advisory?: string | null;
};

export async function fetchActiveStorms(): Promise<Storm[]> {
  const res = await fetch(`${API_BASE}/api/v1/storms/active`);
  if (!res.ok) throw new Error("Failed to fetch active storms");
  return res.json();
}

export async function fetchStorm(stormId: string): Promise<Storm> {
  const res = await fetch(`${API_BASE}/api/v1/storms/${stormId}`);
  if (!res.ok) throw new Error("Failed to fetch storm");
  return res.json();
}

export async function fetchTracks(
  stormId: string,
  limit = 2000
): Promise<TrackPoint[]> {
  const res = await fetch(
    `${API_BASE}/api/v1/storms/${stormId}/tracks?limit=${limit}`
  );
  if (!res.ok) throw new Error("Failed to fetch tracks");
  return res.json();
}

export async function fetchForecasts(
  stormId: string,
  limit = 1000
): Promise<ForecastPoint[]> {
  const res = await fetch(
    `${API_BASE}/api/v1/storms/${stormId}/forecasts?limit=${limit}`
  );
  if (!res.ok) throw new Error("Failed to fetch forecasts");
  return res.json();
}

/* GeoJSON đường đi từ backend đơn giản (nếu dùng) */
export async function fetchStormGeoJSON(
  stormId: string
): Promise<FeatureCollection> {
  const res = await fetch(`${API_BASE}/api/v1/storms/${stormId}/geojson`);
  if (!res.ok) throw new Error("Failed to fetch storm geojson");
  const data = await res.json();
  return data as FeatureCollection;
}
