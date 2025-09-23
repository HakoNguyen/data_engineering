import { LayersControl, TileLayer } from "react-leaflet";

export default function BaseLayers() {
  return (
    <>
      <LayersControl.BaseLayer checked name="Bản đồ thường (OSM)">
        <TileLayer
          attribution="&copy; OpenStreetMap contributors"
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
      </LayersControl.BaseLayer>

      <LayersControl.BaseLayer name="Bản đồ vệ tinh (Esri)">
        <TileLayer
          attribution="Tiles &copy; Esri"
          url="https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}"
        />
      </LayersControl.BaseLayer>
    </>
  );
}
