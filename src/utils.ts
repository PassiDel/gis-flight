import L from 'leaflet';
import type { Flight } from '../server/src/hook.ts';
import planeImg from './plane.png';

export function getPolyline(
  coords: {
    lat: number;
    lon: number;
    altitude: number;
  }[]
) {
  return L.multiOptionsPolyline(
    coords.map((d) => new L.LatLng(d.lat, d.lon, d.altitude)),
    {
      multiOptions: {
        optionIdxFn(latLng) {
          const altThresholdsInFeet = [
            30_000, 20_000, 15_000, 10_000, 7_000, 2_000, 1_000, 500, 0
          ];

          const index = altThresholdsInFeet.findIndex((th) => latLng.alt >= th);
          return index >= 0 ? index : altThresholdsInFeet.length - 1;
        },
        options: [
          { color: '#0000FF' },
          { color: '#0040FF' },
          { color: '#0080FF' },
          { color: '#00FFB0' },
          { color: '#00E000' },
          { color: '#80FF00' },
          { color: '#FFFF00' },
          { color: '#FFC000' },
          { color: '#FFFFFF' }
        ]
      }
    }
  );
}

export function flightToMarker(f: Flight) {
  return L.marker([f.latitude, f.longitude], {
    rotationAngle: f.bearing,
    attribution:
      '<a href="https://www.vecteezy.com/free-png/symbol">Symbol PNGs by Vecteezy</a>',
    icon: L.icon({
      iconUrl: planeImg,
      iconSize: [38 * 2, 32 * 2],
      iconAnchor: [38, 32],
      className: 'plane'
    })
  }).bindPopup(renderPopup(f));
}

export const units = {
  speed: 'kts',
  bearing: '°',
  longitude: '°',
  latitude: '°',
  altitude: 'ft'
} as const;

export function renderPopup(f: Flight) {
  return `<div class="list">${Object.entries(f)
    .map(
      ([k, v]) =>
        `<span>${k}:</span><span>${
          k === 'timestamp'
            ? new Date((v as number) * 1000).toLocaleString()
            : `${v}${units[k as keyof typeof units] === undefined ? '' : ` ${units[k as keyof typeof units]}`}`
        }</span>`
    )
    .join('')}</div>`;
}
