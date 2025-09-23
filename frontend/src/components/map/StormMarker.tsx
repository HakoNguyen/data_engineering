import { Marker, Popup } from "react-leaflet";
import L from "leaflet";
import hurricaneGifUrl from "../../assets/hurricane-maker.gif";

type Storm = {
  name?: string | null;
  storm_id: string;
  basin?: string | null;
  storm_type?: string | null;
  storm_cat?: string | null;
  lat?: number | null;
  lon?: number | null;
};

type Props = { storm?: Storm | null };

export default function StormMarker({ storm }: Props) {
  if (storm?.lat == null || storm?.lon == null) return null;
  const hurricaneIcon = L.divIcon({
    className: "hurricane-marker",
    html: `<img src="${hurricaneGifUrl}" alt="hurricane" />`,
    iconSize: [48, 48],
    iconAnchor: [24, 24],
    popupAnchor: [0, -24],
  });
  return (
    <Marker
      position={[storm.lat as number, storm.lon as number]}
      icon={hurricaneIcon}
    >
      <Popup>
        <div className="text-sm">
          <div className="font-semibold">{storm.name ?? storm.storm_id}</div>
          <div>Basin: {storm.basin ?? "-"}</div>
          <div>
            Type/Cat: {storm.storm_type ?? "-"}/{storm.storm_cat ?? "-"}
          </div>
          <div>
            Lat/Lon: {storm.lat}, {storm.lon}
          </div>
        </div>
      </Popup>
    </Marker>
  );
}
