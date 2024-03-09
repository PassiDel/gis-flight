import './style.css';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import 'leaflet-rotatedmarker';
import 'Leaflet.MultiOptionsPolyline';
import type { Flight } from '../server/src/hook.ts';
import type { Trails } from '../server/src/api.ts';
import markerIcon2x from 'leaflet/dist/images/marker-icon-2x.png';
import markerIcon from 'leaflet/dist/images/marker-icon.png';
import markerShadow from 'leaflet/dist/images/marker-shadow.png';
import { flightToMarker, getPolyline, renderPopup } from './utils.ts';
import { aeroBase, aeroOverlay, Circles, oepnv, osm, zimt } from './layers.ts';

// @ts-ignore
delete L.Icon.Default.prototype._getIconUrl;

L.Icon.Default.mergeOptions({
  iconRetinaUrl: markerIcon2x,
  iconUrl: markerIcon,
  shadowUrl: markerShadow
});

const baseLayers = {
  OpenStreetMap: osm,
  ÖPNV: oepnv,
  Aero: aeroBase
};

const markerGroup = new L.FeatureGroup([]);
const trailsGroup = new L.FeatureGroup([]);
const overlays = {
  VLR: aeroOverlay,
  Circles,
  Trails: trailsGroup,
  Flights: markerGroup
};

const map = L.map('app', {
  center: [52.7924386, 9.930284],
  zoom: 8,
  zoomControl: true,
  layers: [osm, aeroOverlay]
});

const layers = L.control.layers(baseLayers, overlays).addTo(map);

L.marker(zimt).addTo(map);

const baseURL = window.location.hostname;

markerGroup.addTo(map);

const flights = new Map<string, L.Marker>();
const trails = new Map<string, L.MultiOptionsPolyline>();

// Start SSE Stream
const evtSource = new EventSource(
  `http://${baseURL}:3000/api/sse?detailed=true`
);

evtSource.addEventListener('time-update', (event: MessageEvent<string>) => {
  const data = JSON.parse(event.data) as Flight[];
  data.forEach((f) => {
    if (!trails.has(f.id)) {
      const trail = getPolyline([]);
      trail.addTo(trailsGroup);
      trails.set(f.id, trail);
    }
    // Update trail with the latest position
    const trail = trails.get(f.id)!!;
    trail.setLatLngs([
      ...trail.getLatLngs(),
      new L.LatLng(f.latitude, f.longitude, f.altitude)
    ]);
    if (!flights.has(f.id)) {
      const marker = flightToMarker(f);
      marker.addTo(markerGroup);
      flights.set(f.id, marker);
      return;
    }
    // Update Plane marker with the latest position
    const flightMarker = flights.get(f.id)!!;
    flightMarker.setLatLng([f.latitude, f.longitude]);
    flightMarker.setRotationAngle(f.bearing);
    flightMarker.setPopupContent(renderPopup(f));
  });
  // Remove every Plane marker not in the area anymore
  flights.forEach((marker, id) => {
    if (data.findIndex((d) => d.id === id)) {
      return;
    }
    flights.delete(id);
    markerGroup.removeLayer(marker);
  });
});

// Load last 10min of trails
fetch(`http://${baseURL}:3000/api/trails`)
  .then<Trails>((b) => b.json())
  .then((t) => {
    t.forEach((f) => {
      const line = getPolyline(f.pos);
      line.addTo(trailsGroup);
      trails.set(f.flight, line);
    });
  });

// Lazy-load grid
import('./grid.geojson?raw')
  .then((g) => g.default)
  .then((g) => {
    const grid = new L.GeoJSON<{ id: number; x: number; y: number }>(
      JSON.parse(g) as any,
      {
        style: function (_feature) {
          return {
            color: 'green'
          };
        }
      }
    ).bindPopup(function (layer) {
      const { x, y } = (layer as any).feature.properties;
      return `${x} - ${y}`;
    });
    layers.addOverlay(grid, 'Grid');
  });
