import './style.css';
import 'leaflet/dist/leaflet.css';
import L from 'leaflet';
import 'leaflet-rotatedmarker';

const osm = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
  attribution:
    'Kartendaten &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> Mitwirkende'
});

const oepnv = L.tileLayer(
  'https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png',
  {
    attribution:
      'Kartendaten &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> Mitwirkende'
  }
);

const aero = L.tileLayer('overlay/{z}/{x}/{y}.png', {
  attribution:
    '<a href="https://www.openflightmaps.org/copyright">OpenFlightMap</a>',
  maxZoom: 11,
  minZoom: 4
});
const baseLayers = {
  // "Mapbox": mapbox,
  OpenStreetMap: osm,
  ÖPNV: oepnv
};

const overlays = {
  VLR: aero
  // "Roads": roadsLayer
};

const map = L.map('app', {
  center: [52.7924386, 9.930284],
  zoom: 8,
  zoomControl: true,
  layers: [osm, aero]
});

L.control.layers(baseLayers, overlays).addTo(map);

const zimt = new L.LatLng(53.0551608, 8.7835603);
L.marker(zimt).addTo(map);
L.circle(zimt, {
  color: 'green',
  fillColor: '#00ff3366',
  fillOpacity: 0.3,
  radius: 200_000
}).addTo(map);

L.circle(zimt, {
  color: 'blue',
  fillColor: '#3300ff66',
  fillOpacity: 0.3,
  radius: 50_000
}).addTo(map);

L.circle(zimt, {
  color: 'red',
  fillColor: '#ff003366',
  fillOpacity: 0.3,
  radius: 10_000
}).addTo(map);

const data = [
  {
    id: '32c446ab',
    registration: 'D-HABV',
    flight: '',
    callsign: 'LOKI18',
    origin: '',
    destination: '',
    latitude: 52.6388,
    longitude: 13.3216,
    altitude: 1275,
    bearing: 265,
    speed: 98,
    rateOfClimb: 128,
    isOnGround: false,
    squawkCode: '',
    model: 'EC35',
    modeSCode: '3DD2CF',
    radar: 'F-EDDT2',
    isGlider: false,
    timestamp: 1699526792
  }
];

function flightsToMarker(flights: typeof data) {
  return flights.map((f) => {
    return L.marker([f.latitude, f.longitude], {
      rotationAngle: f.bearing,
      attribution:
        '<a href="https://www.vecteezy.com/free-png/symbol">Symbol PNGs by Vecteezy</a>',
      icon: L.icon({
        iconUrl: 'public/plane.png',
        iconSize: [38 * 2, 32 * 2],
        className: 'plane'
      })
    }).bindPopup(
      `${f.registration}: ${f.origin} - ${f.destination}\n${JSON.stringify(
        f,
        undefined,
        2
      )}`
    );
  });
}

const markerGroup = new L.FeatureGroup(flightsToMarker(data));

markerGroup.addTo(map);

const fetchFlights = async () => {
  const bounds = map.getBounds();

  const bound = {
    north: bounds.getNorth(),
    west: bounds.getWest(),
    south: bounds.getSouth(),
    east: bounds.getEast()
  };
  console.log(bound);
  const flights = (await fetch('http://localhost:3000/api/flights', {
    body: JSON.stringify(bound),
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  }).then((b) => b.json())) as typeof data;
  markerGroup.clearLayers();
  flightsToMarker(flights).forEach((m) => markerGroup.addLayer(m));

  console.table(flights);
};
map.on('moveend', fetchFlights);

await fetchFlights();
