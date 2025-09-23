import { LayersControl, TileLayer } from "react-leaflet";

type Props = {
  owmKey?: string;
};

export default function WeatherLayers({ owmKey }: Props) {
  return (
    <>
      {owmKey && (
        <>
          <LayersControl.Overlay name="Weather: Clouds (OWM)">
            <TileLayer
              attribution="Weather tiles © OpenWeatherMap"
              url={`https://tile.openweathermap.org/map/clouds_new/{z}/{x}/{y}.png?appid=${owmKey}`}
              opacity={0.6}
            />
          </LayersControl.Overlay>
          <LayersControl.Overlay name="Weather: Precipitation (OWM)">
            <TileLayer
              attribution="Weather tiles © OpenWeatherMap"
              url={`https://tile.openweathermap.org/map/precipitation_new/{z}/{x}/{y}.png?appid=${owmKey}`}
              opacity={0.6}
            />
          </LayersControl.Overlay>
          <LayersControl.Overlay name="Weather: Wind (OWM)">
            <TileLayer
              attribution="Weather tiles © OpenWeatherMap"
              url={`https://tile.openweathermap.org/map/wind_new/{z}/{x}/{y}.png?appid=${owmKey}`}
              opacity={0.6}
            />
          </LayersControl.Overlay>
          <LayersControl.Overlay name="Weather: Pressure (OWM)">
            <TileLayer
              attribution="Weather tiles © OpenWeatherMap"
              url={`https://tile.openweathermap.org/map/pressure_new/{z}/{x}/{y}.png?appid=${owmKey}`}
              opacity={0.6}
            />
          </LayersControl.Overlay>
          <LayersControl.Overlay name="Weather: Temperature (OWM)">
            <TileLayer
              attribution="Weather tiles © OpenWeatherMap"
              url={`https://tile.openweathermap.org/map/temp_new/{z}/{x}/{y}.png?appid=${owmKey}`}
              opacity={0.6}
            />
          </LayersControl.Overlay>
        </>
      )}

      <LayersControl.Overlay name="Weather: Radar (RainViewer)">
        <TileLayer
          attribution="Radar © RainViewer"
          url="https://tilecache.rainviewer.com/v2/radar/nowcast/0/512/{z}/{x}/{y}.png"
          opacity={0.6}
        />
      </LayersControl.Overlay>
    </>
  );
}
