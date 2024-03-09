import L from 'leaflet';

export const osm = L.tileLayer(
  'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
  {
    attribution:
      'Kartendaten &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> Mitwirkende'
  }
);

export const oepnv = L.tileLayer(
  'https://tileserver.memomaps.de/tilegen/{z}/{x}/{y}.png',
  {
    attribution:
      'Kartendaten &copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> Mitwirkende'
  }
);

export const aeroOverlay = L.tileLayer('overlay/{z}/{x}/{y}.png', {
  attribution:
    '<a href="https://www.openflightmaps.org/copyright">OpenFlightMap</a>',
  maxNativeZoom: 11,
  minNativeZoom: 4,
  noWrap: true,
  bounds: new L.LatLngBounds([47, 5.5], [55, 15])
});

export const aeroBase = L.tileLayer('map/{z}/{x}/{y}.png', {
  attribution:
    '<a href="https://www.openflightmaps.org/copyright">OpenFlightMap</a>',
  maxNativeZoom: 11,
  minNativeZoom: 4,
  noWrap: true,
  bounds: new L.LatLngBounds([47, 5.5], [55, 15])
});
export const zimt = new L.LatLng(53.0551608, 8.7835603);
export const Circles = new L.FeatureGroup([
  L.circle(zimt, {
    color: 'green',
    fillColor: '#00ff3366',
    fillOpacity: 0.3,
    radius: 200_000
  }),
  L.circle(zimt, {
    color: 'blue',
    fillColor: '#3300ff66',
    fillOpacity: 0.3,
    radius: 50_000
  }),
  L.circle(zimt, {
    color: 'red',
    fillColor: '#ff003366',
    fillOpacity: 0.3,
    radius: 10_000
  })
]);
