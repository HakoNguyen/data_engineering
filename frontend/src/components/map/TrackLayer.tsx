import { useMemo } from "react";
import { Marker, Polyline, Popup } from "react-leaflet";
import L from "leaflet";
import hurricaneGifUrl from "../../assets/hurricane-maker.gif";
import type { TrackPoint } from "../../lib/api";

type Props = {
  positions: [number, number][];
  trackPoints?: TrackPoint[];
};

export default function TrackLayer({ positions, trackPoints }: Props) {
  const trackIcon = useMemo(
    () =>
      L.divIcon({
        className: "track-marker",
        html: `<img src="${hurricaneGifUrl}" alt="track" />`,
        iconSize: [24, 24],
        iconAnchor: [12, 12],
        popupAnchor: [0, -12],
      }),
    []
  );
  return (
    <>
      {positions.length > 1 && (
        <Polyline
          positions={positions}
          pathOptions={{ color: "#2563eb", weight: 3 }}
        />
      )}
      {(
        (trackPoints as Array<
          Pick<TrackPoint, "lat" | "lon" | "time" | "wind_speed" | "pressure">
        >) ?? positions.map(([lat, lon]) => ({ lat, lon }))
      ).map((p, idx) => (
        <Marker key={idx} position={[p.lat, p.lon]} icon={trackIcon}>
          <Popup>
            <div className="text-xs">
              <div>
                <b>Point:</b> #{idx + 1}
              </div>
              {"time" in p && p.time && (
                <div>
                  <b>Time:</b> {String(p.time)}
                </div>
              )}
              {"wind_speed" in p && p.wind_speed != null && (
                <div>
                  <b>Wind:</b> {String(p.wind_speed)} kt
                </div>
              )}
              {"pressure" in p && p.pressure != null && (
                <div>
                  <b>Pressure:</b> {p.pressure} mb
                </div>
              )}
              <div>
                <b>Lat:</b> {Number(p.lat).toFixed(2)}
              </div>
              <div>
                <b>Lon:</b> {Number(p.lon).toFixed(2)}
              </div>
            </div>
          </Popup>
        </Marker>
      ))}
    </>
  );
}
