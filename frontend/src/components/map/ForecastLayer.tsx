import { useMemo } from "react";
import { LayersControl, Marker, Polyline, Popup } from "react-leaflet";
import L from "leaflet";
import hurricaneGifUrl from "../../assets/hurricane-maker.gif";

type ForecastPoint = {
  lat?: number | null;
  lon?: number | null;
  forecast_time?: string | null;
  wind_speed?: number | null;
  pressure?: number | null;
  storm_type?: string | null;
  storm_cat?: string | null;
  advisory?: string | null;
};

type Props = {
  positions: [number, number][];
  forecasts: ForecastPoint[];
};

export default function ForecastLayer({ positions, forecasts }: Props) {
  const forecastIcon = useMemo(
    () =>
      L.divIcon({
        className: "forecast-marker",
        html: `<img src="${hurricaneGifUrl}" alt="forecast" />`,
        iconSize: [32, 32],
        iconAnchor: [16, 16],
        popupAnchor: [0, -16],
      }),
    []
  );
  return (
    <LayersControl.Overlay name="Dự báo (Forecast)">
      <>
        {positions.length > 1 && (
          <Polyline
            positions={positions}
            pathOptions={{ color: "#f59e0b", dashArray: "6 6", weight: 3 }}
          />
        )}
        {forecasts.map((f, idx) =>
          f.lat != null && f.lon != null ? (
            <Marker
              key={idx}
              position={[f.lat as number, f.lon as number]}
              icon={forecastIcon}
            >
              <Popup>
                <div className="text-sm">
                  <div>
                    <b>Thời gian:</b> {f.forecast_time ?? "-"}
                  </div>
                  <div>
                    <b>Gió:</b> {f.wind_speed ?? "-"} kt
                  </div>
                  <div>
                    <b>Áp suất:</b> {f.pressure ?? "-"} mb
                  </div>
                  <div>
                    <b>Loại/Cấp:</b> {f.storm_type ?? "-"} /{" "}
                    {f.storm_cat ?? "-"}
                  </div>
                  <div>
                    <b>Advisory:</b> {f.advisory ?? "-"}
                  </div>
                </div>
              </Popup>
            </Marker>
          ) : null
        )}
      </>
    </LayersControl.Overlay>
  );
}
